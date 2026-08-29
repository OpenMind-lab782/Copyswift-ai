// CopySwiftAI Document Studio - Immutable overlay renderer
// Usage: mutool run apply_overlay.js <input.pdf> <ops_json_string> <output.pdf>

var B64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
var B64_LOOKUP = {}
for (var bi = 0; bi < B64_CHARS.length; bi++) {
    B64_LOOKUP[B64_CHARS.charAt(bi)] = bi
}

function base64ToBytes(b64) {
    var clean = b64.replace(/=+$/, "")
    var bytes = []
    var buffer = 0
    var bitsCollected = 0

    for (var i = 0; i < clean.length; i++) {
        var value = B64_LOOKUP[clean.charAt(i)]
        if (value === undefined) continue
        buffer = (buffer << 6) | value
        bitsCollected += 6
        if (bitsCollected >= 8) {
            bitsCollected -= 8
            bytes.push((buffer >> bitsCollected) & 0xFF)
        }
    }
    return bytes
}

var input_path = scriptArgs[0]
var ops_json = scriptArgs[1]
var output_path = scriptArgs[2]

var doc = new mupdf.PDFDocument(input_path)
var ops = JSON.parse(ops_json)

for (var i = 0; i < ops.pages.length; i++) {
    var page_ops = ops.pages[i]
    var page = doc.loadPage(page_ops.page_index)
    var pageObj = page.getObject()

    // Step 1a: redact text-related regions - imageMethod=0 protects
    // any images/backgrounds that happen to sit under edited text.
    for (var r = 0; r < page_ops.redact_rects_text.length; r++) {
        var rect = page_ops.redact_rects_text[r]
        var annot = page.createAnnotation("Redact")
        annot.setRect(rect)
    }
    if (page_ops.redact_rects_text.length > 0) {
        page.applyRedactions(false, 0, 0, 0)
    }

    // Step 1b: redact image-related regions - imageMethod=2 actually
    // strips the image content within these specific rects (used only
    // for images being deleted or replaced).
    for (var ri = 0; ri < page_ops.redact_rects_image.length; ri++) {
        var rectI = page_ops.redact_rects_image[ri]
        var annotI = page.createAnnotation("Redact")
        annotI.setRect(rectI)
    }
    if (page_ops.redact_rects_image.length > 0) {
        page.applyRedactions(false, 2, 0, 0)
    }

    var buf = new mupdf.Buffer()
    var hasContent = false

    // Step 2: append new/edited text as a fresh content stream
    if (page_ops.text_inserts.length > 0) {
        var fontRefs = {}
        for (var t = 0; t < page_ops.text_inserts.length; t++) {
            var item = page_ops.text_inserts[t]
            var fontKey = item.font || "Helvetica"

            if (!fontRefs[fontKey]) {
                var fontObj = doc.addObject({
                    Type: "Font",
                    Subtype: "Type1",
                    BaseFont: fontKey
                })
                fontRefs[fontKey] = fontObj
            }

            var r2 = ((item.color >> 16) & 255) / 255
            var g2 = ((item.color >> 8) & 255) / 255
            var b2 = (item.color & 255) / 255

            buf.writeLine(
                r2.toFixed(4) + " " + g2.toFixed(4) + " " + b2.toFixed(4) + " rg " +
                "BT /F" + t + " " + item.font_size + " Tf " +
                item.x.toFixed(2) + " " + item.y.toFixed(2) + " Td " +
                "(" + item.content.replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)") + ") Tj ET"
            )
            hasContent = true
        }

        if (!pageObj.Resources.Font) {
            pageObj.Resources.Font = doc.addObject({})
        }
        for (var t2 = 0; t2 < page_ops.text_inserts.length; t2++) {
            var fontKey2 = page_ops.text_inserts[t2].font || "Helvetica"
            pageObj.Resources.Font["F" + t2] = fontRefs[fontKey2]
        }
    }

    // Step 3: insert new/edited images
    if (page_ops.image_inserts.length > 0) {
        if (!pageObj.Resources.XObject) {
            pageObj.Resources.XObject = doc.addObject({})
        }

        for (var m = 0; m < page_ops.image_inserts.length; m++) {
            var imgItem = page_ops.image_inserts[m]
            var imgBytes = base64ToBytes(imgItem.png_base64)

            var imgBuf = new mupdf.Buffer()
            for (var bIdx = 0; bIdx < imgBytes.length; bIdx++) {
                imgBuf.writeByte(imgBytes[bIdx])
            }

            var fzImage = new mupdf.Image(imgBuf)
            var imgRef = doc.addImage(fzImage)

            var imgName = "Img" + m
            pageObj.Resources.XObject[imgName] = imgRef

            buf.writeLine(
                "q " + imgItem.width.toFixed(2) + " 0 0 " + imgItem.height.toFixed(2) +
                " " + imgItem.x.toFixed(2) + " " + imgItem.y.toFixed(2) + " cm /" + imgName + " Do Q"
            )
            hasContent = true
        }
    }

    if (hasContent) {
        var newContentRef = doc.addStream(buf)

        if (pageObj.Contents) {
            pageObj.Contents = [pageObj.Contents, newContentRef]
        } else {
            pageObj.Contents = newContentRef
        }
    }
}

// Step 4: embed the immutability audit trail into document metadata.
// This travels with the file as inspectable proof of when it was
// generated and what original-content hash it was verified against.
if (ops.audit) {
    try {
        doc.setMetaData("info:CopySwiftAIOriginalSHA256", ops.audit.original_sha256 || "")
        doc.setMetaData("info:CopySwiftAIGeneratedAt", ops.audit.generated_at || "")
        doc.setMetaData("info:CopySwiftAIEngine", "CopySwiftAI Document Studio - mutool overlay v1")
    } catch (e) {
        // Metadata embedding is best-effort; must not block the render.
    }
}

doc.save(output_path, "")
print("RENDER_OK")
