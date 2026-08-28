// CopySwiftAI Document Studio - Immutable overlay renderer
// Usage: mutool run apply_overlay.js <input.pdf> <ops.json> <output.pdf>

var input_path = scriptArgs[0]
var ops_json = scriptArgs[1]
var output_path = scriptArgs[2]

var doc = new mupdf.PDFDocument(input_path)
var ops = JSON.parse(ops_json)

for (var i = 0; i < ops.pages.length; i++) {
    var page_ops = ops.pages[i]
    var page = doc.loadPage(page_ops.page_index)
    var pageObj = page.getObject()

    // Step 1: mark old text regions for redaction (text-only, backgrounds untouched)
    for (var r = 0; r < page_ops.redact_rects.length; r++) {
        var rect = page_ops.redact_rects[r]
        var annot = page.createAnnotation("Redact")
        annot.setRect(rect)
    }
    if (page_ops.redact_rects.length > 0) {
        page.applyRedactions(false, 0, 0, 0)
    }

    // Step 2: append new/edited text as a fresh content stream (original stream untouched)
    if (page_ops.text_inserts.length > 0) {
        var buf = new mupdf.Buffer()

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
        }

        var newContentRef = doc.addStream(buf)

        var res = pageObj.Resources
        if (!res.Font) {
            res.Font = doc.addObject({})
        }
        for (var t2 = 0; t2 < page_ops.text_inserts.length; t2++) {
            var fontKey2 = page_ops.text_inserts[t2].font || "Helvetica"
            res.Font["F" + t2] = fontRefs[fontKey2]
        }

        if (pageObj.Contents) {
            pageObj.Contents = [pageObj.Contents, newContentRef]
        } else {
            pageObj.Contents = newContentRef
        }
    }
}

doc.save(output_path, "")
print("RENDER_OK")
