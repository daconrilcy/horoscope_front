import { z } from 'zod';
import { http } from './client';
import { ApiError } from './errors';

/**
 * Schémas Zod pour validation stricte (fail-fast)
 */

/**
 * Schéma pour les erreurs de champ (field errors)
 */
export const FieldErrorsSchema = z.record(z.string(), z.array(z.string()).nonempty()).optional();

/**
 * Schéma pour la structure d'erreur API
 */
export const ErrorShapeSchema = z.object({
  message: z.string().min(1),
  request_id: z.string().optional(),
  code: z.string().optional(),
  details: FieldErrorsSchema,
});

/**
 * Schéma pour un utilisateur
 */
const UserSchema = z.object({
  id: z.string().uuid().or(z.string().min(1)),
  email: z.string().email(),
});

/**
 * Schéma pour la réponse de login
 */
export const LoginResponseSchema = z.object({
  token: z.string().min(10),
  user: UserSchema,
});

/**
 * Schéma pour la réponse de signup (identique à login)
 */
export const SignupResponseSchema = LoginResponseSchema;

/**
 * Schéma pour la réponse de requestReset
 */
export const RequestResetResponseSchema = z.object({
  message: z.string().min(1),
});

/**
 * Schéma pour la réponse de confirmReset
 */
export const ConfirmResetResponseSchema = z.object({
  message: z.string().min(1),
});

/**
 * Types inférés depuis les schémas Zod
 */
export type LoginResponse = z.infer<typeof LoginResponseSchema>;
export type SignupResponse = z.infer<typeof SignupResponseSchema>;
export type RequestResetResponse = z.infer<typeof RequestResetResponseSchema>;
export type ConfirmResetResponse = z.infer<typeof ConfirmResetResponseSchema>;
export type FieldErrors = z.infer<typeof FieldErrorsSchema>;
export type ErrorShape = z.infer<typeof ErrorShapeSchema>;

/**
 * Service d'authentification
 * Endpoints : /v1/auth/*
 */
export const authService = {
  /**
   * Inscription d'un nouvel utilisateur
   * @param email Email de l'utilisateur (sera normalisé côté page)
   * @param password Mot de passe
   * @returns Réponse validée avec token et user
   * @throws ApiError si erreur API (401, 422, etc.)
   * @throws NetworkError si erreur réseau
   */
  async signup(email: string, password: string): Promise<SignupResponse> {
    try {
      const response = await http.post<unknown>('/v1/auth/signup', {
        email,
        password,
      }, { auth: false });

      // Validation Zod stricte (fail-fast)
      const validated = SignupResponseSchema.parse(response);
      return validated;
    } catch (error) {
      // Si c'est une ApiError avec details, enrichir avec les details parsés
      if (error instanceof ApiError && error.details != null) {
        // Les details sont déjà dans error.details, on peut les utiliser directement
        throw error;
      }
      throw error;
    }
  },

  /**
   * Connexion d'un utilisateur
   * @param email Email de l'utilisateur (sera normalisé côté page)
   * @param password Mot de passe
   * @returns Réponse validée avec token et user
   * @throws ApiError si erreur API (401, 422, etc.)
   * @throws NetworkError si erreur réseau
   */
  async login(email: string, password: string): Promise<LoginResponse> {
    try {
      const response = await http.post<unknown>('/v1/auth/login', {
        email,
        password,
      }, { auth: false });

      // Validation Zod stricte (fail-fast)
      const validated = LoginResponseSchema.parse(response);
      return validated;
    } catch (error) {
      // Si c'est une ApiError avec details, enrichir avec les details parsés
      if (error instanceof ApiError && error.details != null) {
        // Les details sont déjà dans error.details, on peut les utiliser directement
        throw error;
      }
      throw error;
    }
  },

  /**
   * Demande de réinitialisation de mot de passe
   * @param email Email de l'utilisateur (sera normalisé côté page)
   * @returns Réponse validée avec message
   * @throws ApiError si erreur API (400, 422, etc.)
   * @throws NetworkError si erreur réseau
   */
  async requestReset(email: string): Promise<RequestResetResponse> {
    try {
      const response = await http.post<unknown>('/v1/auth/reset/request', {
        email,
      }, { auth: false });

      // Validation Zod stricte (fail-fast)
      const validated = RequestResetResponseSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof ApiError && error.details) {
        throw error;
      }
      throw error;
    }
  },

  /**
   * Confirmation de réinitialisation de mot de passe
   * @param token Token de réinitialisation (depuis URL)
   * @param password Nouveau mot de passe
   * @returns Réponse validée avec message
   * @throws ApiError si erreur API (400, 422, etc.)
   * @throws NetworkError si erreur réseau
   */
  async confirmReset(token: string, password: string): Promise<ConfirmResetResponse> {
    try {
      const response = await http.post<unknown>('/v1/auth/reset/confirm', {
        token,
        password,
      }, { auth: false });

      // Validation Zod stricte (fail-fast)
      const validated = ConfirmResetResponseSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof ApiError && error.details) {
        throw error;
      }
      throw error;
    }
  },
};

