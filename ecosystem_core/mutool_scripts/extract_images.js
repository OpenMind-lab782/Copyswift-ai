// CopySwiftAI Document Studio - Image extraction via device callback
// Usage: mutool run extract_images.js <input.pdf>
// Outputs JSON to stdout: {"pages": [{"page_index": 0, "images": [{"x":.., "y":.., "width":.., "height":.., "png_base64": "..."}]}]}

var B64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

function bufferToBase64(buf) {
    var result = ""
    var len = buf.length
    for (var i = 0; i < len; i += 3) {
        var b0 = buf[i]
        var b1 = (i + 1 < len) ? buf[i + 1] : 0
        var b2 = (i + 2 < len) ? buf[i + 2] : 0

        result += B64_CHARS.charAt(b0 >> 2)
        result += B64_CHARS.charAt(((b0 & 3) << 4) | (b1 >> 4))
        result += (i + 1 < len) ? B64_CHARS.charAt(((b1 & 15) << 2) | (b2 >> 6)) : "="
        result += (i + 2 < len) ? B64_CHARS.charAt(b2 & 63) : "="
    }
    return result
}

function escapeJsonString(s) {
    return s.replace(/[\\"]/g, "\\$&").replace(/\n/g, "\\n").replace(/\r/g, "\\r")
}

var input_path = scriptArgs[0]
var doc = new mupdf.PDFDocument(input_path)

var pageCount = doc.countPages()
var pagesOutput = []

for (var p = 0; p < pageCount; p++) {
    var page = doc.loadPage(p)
    var bounds = page.getBounds()
    var pageHeight = bounds[3] - bounds[1]

    var imagesFound = []

    var device = {
        fillImage: function(image, ctm) {
            var pix = image.toPixmap()
            var pngBuf = pix.asPNG()
            var b64 = bufferToBase64(pngBuf)

            var a = ctm[0]
            var d = ctm[3]
            var e = ctm[4]
            var f = ctm[5]

            var widthPdf = a
            var heightPdf = d
            var xPdf = e
            var yPdfBottom = f

            var yTop = pageHeight - (yPdfBottom + heightPdf)

            imagesFound.push({
                x: xPdf,
                y: yTop,
                width: widthPdf,
                height: heightPdf,
                png_base64: b64
            })
        }
    }

    page.run(device, mupdf.Matrix.identity)

    var imageStrs = []
    for (var i = 0; i < imagesFound.length; i++) {
        var img = imagesFound[i]
        imageStrs.push(
            '{"x":' + img.x + ',"y":' + img.y +
            ',"width":' + img.width + ',"height":' + img.height +
            ',"png_base64":"' + img.png_base64 + '"}'
        )
    }

    pagesOutput.push('{"page_index":' + p + ',"images":[' + imageStrs.join(",") + ']}')
}

print('{"pages":[' + pagesOutput.join(",") + ']}')
