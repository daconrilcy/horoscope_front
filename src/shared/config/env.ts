import { z } from 'zod';

const envSchema = z.object({
  VITE_API_BASE_URL: z.string().url({
    message: 'VITE_API_BASE_URL must be a valid URL',
  }),
});

type Env = z.infer<typeof envSchema>;

function getEnv(): Env {
  const raw = {
    VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
  };

  const result = envSchema.safeParse(raw);

  if (!result.success) {
    const errors = result.error.errors.map((err) => {
      return `${err.path.join('.')}: ${err.message}`;
    });

    throw new Error(
      `❌ Configuration d'environnement invalide:\n${errors.join('\n')}\n\n` +
        'Veuillez définir toutes les variables requises dans votre fichier .env'
    );
  }

  return result.data;
}

export const env = getEnv();

