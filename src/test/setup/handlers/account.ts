import { http, HttpResponse } from 'msw';

const API_BASE_URL = 'http://localhost:8000';

export const handlers = [
  // GET /v1/account/export
  http.get(`${API_BASE_URL}/v1/account/export`, async () => {
    // Créer un blob ZIP simulé
    const zipContent =
      'PK\x03\x04\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00data.txt\x00\x00';
    const blob = new Blob([zipContent], { type: 'application/zip' });

    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const filename = `account-export-${year}${month}${day}.zip`;

    // eslint-disable-next-line @typescript-eslint/no-unsafe-return, @typescript-eslint/no-unsafe-call
    return HttpResponse.body(await blob.arrayBuffer(), {
      headers: {
        'Content-Type': 'application/zip',
        'Content-Disposition': `attachment; filename="${filename}"`,
      },
    });
  }),

  // DELETE /v1/account
  http.delete(`${API_BASE_URL}/v1/account`, () => {
    // Simuler 409 si opération en cours
    const shouldConflict = Math.random() < 0.1; // 10% de chance pour test
    if (shouldConflict) {
      return HttpResponse.json(
        {
          message:
            'Suppression impossible pour le moment (opérations en cours)',
          code: 'conflict',
        },
        { status: 409 }
      );
    }

    // Succès (204 No Content)
    return new HttpResponse(null, { status: 204 });
  }),
];
