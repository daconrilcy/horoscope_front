import { http, HttpResponse } from 'msw';

const API_BASE_URL = 'http://localhost:8000';

const sampleLegalHtml = `
<!DOCTYPE html>
<html>
<head><title>Legal Document</title></head>
<body>
  <h1>Terms of Service</h1>
  <p>This is a sample legal document.</p>
</body>
</html>
`;

export const handlers = [
  // GET /v1/legal/tos
  http.get(`${API_BASE_URL}/v1/legal/tos`, () => {
    return HttpResponse.text(sampleLegalHtml, {
      headers: {
        'Content-Type': 'text/html',
        ETag: '"legal-tos-v1"',
        'Last-Modified': new Date().toUTCString(),
        'X-Legal-Version': '1.0',
      },
    });
  }),

  // GET /v1/legal/privacy
  http.get(`${API_BASE_URL}/v1/legal/privacy`, () => {
    return HttpResponse.text(
      sampleLegalHtml.replace('Terms of Service', 'Privacy Policy'),
      {
        headers: {
          'Content-Type': 'text/html',
          ETag: '"legal-privacy-v1"',
          'Last-Modified': new Date().toUTCString(),
          'X-Legal-Version': '1.0',
        },
      }
    );
  }),
];
