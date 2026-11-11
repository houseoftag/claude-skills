// vt_denoise: Apple's ML temporal noise filter (VideoToolbox VTTemporalNoiseFilter, macOS 26+) as a pipe filter.
//
// Build (source only is shipped; compile on the machine that will run it):
//   xcrun swiftc -O vtnr/main.swift -o vt_denoise
//
// Use (8-bit NV12, video range, in and out; one shot per call):
//   ffmpeg -i IN -vf scale=1920:1080,format=nv12 -f rawvideo - | ./vt_denoise 1920 1080 0.85 | \
//     ffmpeg -f rawvideo -pix_fmt nv12 -s 1920x1080 -r 24 -i - -c:v libx264 out.mp4
//   STRENGTH is 0-1; a negative value is a test mode (pixel transfers only, no filtering).
//
// Design notes (keep these when you edit):
//   * One shot per call. Each frame is filtered with 1 previous and 2 next reference frames (the processor's
//     maximum), so references must never cross a cut: start a new process for every shot.
//   * The processor only accepts Apple's compressed (lossless) pixel formats, so frames move in and out with a
//     VTPixelTransferSession.
//   * Every buffer is tagged Rec.709 video range (tag709) so VideoToolbox never converts between colour
//     standards.
//   * The whole shot is read into memory first (shots are at most a few hundred frames).
//   * A 1-frame shot passes through unfiltered (the filter needs at least one reference frame).
//   * Strength 0.85 was the calibrated default (calibrated on a Sony A7IV 4K -> 1080p job, 2026-10): 1.0 removed no
//     more noise in measurement and 0.85 keeps more texture. On 200 % crops it matched a heavy per-frame neural
//     denoiser at about 150x the speed.
import Foundation
import VideoToolbox
import CoreVideo
import CoreMedia

func fail(_ msg: String) -> Never {
    FileHandle.standardError.write((msg + "\n").data(using: .utf8)!)
    exit(1)
}

func makePool(_ attrs: [String: Any], _ w: Int, _ h: Int) -> CVPixelBufferPool {
    var a = attrs
    a[kCVPixelBufferWidthKey as String] = w
    a[kCVPixelBufferHeightKey as String] = h
    if a[kCVPixelBufferIOSurfacePropertiesKey as String] == nil { a[kCVPixelBufferIOSurfacePropertiesKey as String] = [String: Any]() }
    var pool: CVPixelBufferPool?
    guard CVPixelBufferPoolCreate(nil, nil, a as CFDictionary, &pool) == kCVReturnSuccess, let p = pool else { fail("pool create failed") }
    return p
}

// Tag every buffer as Rec.709 video range so VideoToolbox never converts between colour standards.
func tag709(_ buf: CVPixelBuffer) {
    CVBufferSetAttachment(buf, kCVImageBufferYCbCrMatrixKey, kCVImageBufferYCbCrMatrix_ITU_R_709_2, .shouldPropagate)
    CVBufferSetAttachment(buf, kCVImageBufferColorPrimariesKey, kCVImageBufferColorPrimaries_ITU_R_709_2, .shouldPropagate)
    CVBufferSetAttachment(buf, kCVImageBufferTransferFunctionKey, kCVImageBufferTransferFunction_ITU_R_709_2, .shouldPropagate)
}

func buffer(_ pool: CVPixelBufferPool) -> CVPixelBuffer {
    var b: CVPixelBuffer?
    guard CVPixelBufferPoolCreatePixelBuffer(nil, pool, &b) == kCVReturnSuccess, let buf = b else { fail("buffer create failed") }
    tag709(buf)
    return buf
}

func readExactly(_ n: Int) -> Data? {
    var d = Data(capacity: n)
    while d.count < n {
        let chunk = FileHandle.standardInput.readData(ofLength: n - d.count)
        if chunk.isEmpty { return d.isEmpty ? nil : nil }
        d.append(chunk)
    }
    return d
}

// copy packed NV12 bytes <-> a '420v' pixel buffer (row strides differ)
func fill(_ buf: CVPixelBuffer, from d: Data, w: Int, h: Int) {
    CVPixelBufferLockBaseAddress(buf, [])
    d.withUnsafeBytes { (src: UnsafeRawBufferPointer) in
        for plane in 0..<2 {
            let rows = plane == 0 ? h : h / 2
            let dst = CVPixelBufferGetBaseAddressOfPlane(buf, plane)!
            let stride = CVPixelBufferGetBytesPerRowOfPlane(buf, plane)
            let off = plane == 0 ? 0 : w * h
            for r in 0..<rows { memcpy(dst + r * stride, src.baseAddress! + off + r * w, w) }
        }
    }
    CVPixelBufferUnlockBaseAddress(buf, [])
}

func dump(_ buf: CVPixelBuffer, w: Int, h: Int) {
    CVPixelBufferLockBaseAddress(buf, .readOnly)
    var out = Data(count: w * h * 3 / 2)
    out.withUnsafeMutableBytes { (dst: UnsafeMutableRawBufferPointer) in
        for plane in 0..<2 {
            let rows = plane == 0 ? h : h / 2
            let src = CVPixelBufferGetBaseAddressOfPlane(buf, plane)!
            let stride = CVPixelBufferGetBytesPerRowOfPlane(buf, plane)
            let off = plane == 0 ? 0 : w * h
            for r in 0..<rows { memcpy(dst.baseAddress! + off + r * w, src + r * stride, w) }
        }
    }
    CVPixelBufferUnlockBaseAddress(buf, .readOnly)
    FileHandle.standardOutput.write(out)
}

let args = CommandLine.arguments
guard args.count >= 4, let w = Int(args[1]), let h = Int(args[2]), let strength = Float(args[3]) else {
    fail("usage: vt_denoise WIDTH HEIGHT STRENGTH(0-1) < nv12 > nv12")
}
let fmt = kCVPixelFormatType_Lossless_420YpCbCr8BiPlanarVideoRange
guard VTTemporalNoiseFilterConfiguration.isSupported,
      let cfg = VTTemporalNoiseFilterConfiguration(frameWidth: w, frameHeight: h, sourcePixelFormat: fmt) else {
    fail("temporal noise filter not supported for \(w)x\(h)")
}
let nPrev = cfg.previousFrameCount ?? 1, nNext = cfg.nextFrameCount ?? 2
let srcPool = makePool(cfg.sourcePixelBufferAttributes, w, h)
let dstPool = makePool(cfg.destinationPixelBufferAttributes, w, h)
let plainPool = makePool([kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_420YpCbCr8BiPlanarVideoRange], w, h)
var xferOut: VTPixelTransferSession?
guard VTPixelTransferSessionCreate(allocator: nil, pixelTransferSessionOut: &xferOut) == noErr, let xfer = xferOut else { fail("transfer session failed") }

// read the whole shot (shots are at most a few hundred frames)
var frames: [CVPixelBuffer] = []
let frameBytes = w * h * 3 / 2
while let d = readExactly(frameBytes) {
    let plain = buffer(plainPool)
    fill(plain, from: d, w: w, h: h)
    let comp = buffer(srcPool)
    guard VTPixelTransferSessionTransferImage(xfer, from: plain, to: comp) == noErr else { fail("transfer in failed") }
    frames.append(comp)
}
if frames.isEmpty { exit(0) }

let processor = VTFrameProcessor()
do { try processor.startSession(configuration: cfg) } catch { fail("start session: \(error)") }
let ts = { (i: Int) in CMTime(value: CMTimeValue(i), timescale: 30) }
let sema = DispatchSemaphore(value: 0)
Task {
    for i in 0..<frames.count {
        let src = VTFrameProcessorFrame(buffer: frames[i], presentationTimeStamp: ts(i))!
        let prev = (max(0, i - nPrev)..<i).map { VTFrameProcessorFrame(buffer: frames[$0], presentationTimeStamp: ts($0))! }
        let next = ((i + 1)..<min(frames.count, i + 1 + nNext)).map { VTFrameProcessorFrame(buffer: frames[$0], presentationTimeStamp: ts($0))! }
        let dst = buffer(dstPool)
        let dstFrame = VTFrameProcessorFrame(buffer: dst, presentationTimeStamp: ts(i))!
        // at least one reference frame is required; a 1-frame shot passes through unfiltered.
        // A negative strength is a test mode: transfers only, no filtering.
        if (prev.isEmpty && next.isEmpty) || strength < 0 {
            let plain = buffer(plainPool)
            _ = VTPixelTransferSessionTransferImage(xfer, from: frames[i], to: plain)
            dump(plain, w: w, h: h); continue
        }
        guard let p = VTTemporalNoiseFilterParameters(sourceFrame: src, nextFrames: next, previousFrames: prev,
                                                      destinationFrame: dstFrame, filterStrength: strength,
                                                      hasDiscontinuity: i == 0) else { fail("parameters failed at frame \(i)") }
        do { _ = try await processor.process(parameters: p) } catch { fail("process failed at frame \(i): \(error)") }
        let plain = buffer(plainPool)
        guard VTPixelTransferSessionTransferImage(xfer, from: dst, to: plain) == noErr else { fail("transfer out failed") }
        dump(plain, w: w, h: h)
    }
    processor.endSession()
    sema.signal()
}
sema.wait()
