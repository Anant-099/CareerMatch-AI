from pypdf import PdfWriter
import unittest
from io import BytesIO

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def make_test_pdf() -> bytes:
    """Create a tiny PDF containing selectable resume text."""
    content = b"BT /F1 12 Tf 50 740 Td (Python SQL FastAPI Git) Tj ET"

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R "
            b"/MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 5 0 R >> >> "
            b"/Contents 4 0 R >>"
        ),
        (
            b"<< /Length " + str(len(content)).encode()
            + b" >>\nstream\n" + content + b"\nendstream"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]

    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode())
        pdf.extend(obj + b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")

    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())

    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode()
    )

    return bytes(pdf)

class TestCareerMatchAPI(unittest.TestCase):

    def test_health_endpoint(self):
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_missing_resume(self):
        response = client.post(
            "/api/analyze",
            data={"job_description": "Python developer"}
        )
        self.assertEqual(response.status_code, 422)

    def test_empty_job_description(self):
        response = client.post(
            "/api/analyze",
            files={
                "resume": (
                    "resume.pdf",
                    BytesIO(b"fake pdf"),
                    "application/pdf",
                )
            },
            data={"job_description": "   "}
        )
        self.assertEqual(response.status_code, 400)

    def test_wrong_file_type(self):
        response = client.post(
            "/api/analyze",
            files={
                "resume": (
                    "resume.txt",
                    BytesIO(b"not a PDF"),
                    "text/plain",
                )
            },
            data={"job_description": "Python developer"}
        )
        self.assertEqual(response.status_code, 400)


    def test_successful_resume_analysis(self):
        response = client.post(
            "/api/analyze",
            files={
                "resume": (
                    "test_resume.pdf",
                    BytesIO(make_test_pdf()),
                    "application/pdf",
                )
            },
            data={
                "job_description": (
                    "Python SQL FastAPI Docker"
                )
            },
        )

        self.assertEqual(response.status_code, 200)

        result = response.json()

        self.assertIn("match_score", result)
        self.assertGreaterEqual(result["match_score"], 0)
        self.assertLessEqual(result["match_score"], 100)

        self.assertIn("python", result["resume_skills"])
        self.assertIn("matched_skills", result)
        self.assertIn("missing_skills", result)

        self.assertIn("python", result["matched_skills"])
        self.assertIn("docker", result["missing_skills"])


    def test_history_endpoint_returns_list(self):
        response = client.get("/api/history")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)


    def test_history_contains_saved_analysis(self):
        # Create a new analysis specifically for this test.
        analysis_response = client.post(
            "/api/analyze",
            files={
                "resume": (
                    "history_test_resume.pdf",
                    BytesIO(make_test_pdf()),
                    "application/pdf",
                )
            },
            data={
                "job_description": "Python SQL FastAPI Docker"
            },
        )

        self.assertEqual(analysis_response.status_code, 200)

        # Retrieve history and find the analysis created above.
        response = client.get("/api/history")

        self.assertEqual(response.status_code, 200)

        records = response.json()
        record = next(
            (
                item
                for item in records
                if item["filename"] == "history_test_resume.pdf"
            ),
            None,
        )

        self.assertIsNotNone(
            record,
            "The newly created analysis should appear in history",
        )
        self.assertIn("match_score", record)
        self.assertIn("created_at", record)
        self.assertIn("result", record)



if __name__ == "__main__":
    unittest.main()
