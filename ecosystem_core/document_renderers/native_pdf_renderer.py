class NativePDFRenderer:
    def render(self, document, output_name="output.pdf"):
        if not isinstance(document, dict):
            raise TypeError("Document must be a dictionary.")
        pages = document.get("pages") or []
        objects = {
            1: b"<< /Type /Catalog /Pages 2 0 R >>",
            2: b"",
            3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        }
        page_refs = []
        for index, page in enumerate(pages):
            width = float(page.get("width") or 595)
            height = float(page.get("height") or 842)
            commands = []
            for element in page.get("elements") or []:
                if str(element.get("type", "")).lower() != "text":
                    continue
                text = str(element.get("content", "")).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").replace("\n", " ").replace("\r", " ")
                x = float(element.get("x", 0))
                y = height - float(element.get("y", 0))
                size = float(element.get("font_size") or 12)
                color = element.get("color", 0)
                if isinstance(color, int):
                    r = ((color >> 16) & 255) / 255
                    g = ((color >> 8) & 255) / 255
                    b = (color & 255) / 255
                elif isinstance(color, str) and color.startswith("#") and len(color) == 7:
                    r = int(color[1:3], 16) / 255
                    g = int(color[3:5], 16) / 255
                    b = int(color[5:7], 16) / 255
                else:
                    r = g = b = 0
                commands.append(f"BT {r:.4f} {g:.4f} {b:.4f} rg /F1 {size:.2f} Tf 1 0 0 1 {x:.2f} {y:.2f} Tm ({text}) Tj ET")
            content_ref = 4 + index * 2
            page_ref = content_ref + 1
            content = "\n".join(commands).encode("latin-1", "replace")
            objects[content_ref] = f"<< /Length {len(content)} >>\nstream\n".encode() + content + b"\nendstream"
            objects[page_ref] = f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width:.2f} {height:.2f}] /Resources << /Font << /F1 3 0 R >> >> /Contents {content_ref} 0 R >>".encode()
            page_refs.append(page_ref)
        kids = " ".join(f"{ref} 0 R" for ref in page_refs)
        objects[2] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_refs)} >>".encode()
        max_ref = max(objects)
        pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0] * (max_ref + 1)
        for ref in range(1, max_ref + 1):
            offsets[ref] = len(pdf)
            pdf.extend(f"{ref} 0 obj\n".encode())
            pdf.extend(objects[ref])
            pdf.extend(b"\nendobj\n")
        xref = len(pdf)
        pdf.extend(f"xref\n0 {max_ref + 1}\n0000000000 65535 f \n".encode())
        for ref in range(1, max_ref + 1):
            pdf.extend(f"{offsets[ref]:010d} 00000 n \n".encode())
        pdf.extend(f"trailer\n<< /Size {max_ref + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
        return bytes(pdf)
