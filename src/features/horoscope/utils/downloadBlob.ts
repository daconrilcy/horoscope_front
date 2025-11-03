/**
 * Helper pour télécharger un blob en tant que fichier
 * Crée un lien temporaire, déclenche le téléchargement, puis nettoie
 * @param blob Blob à télécharger
 * @param filename Nom du fichier pour le téléchargement
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
