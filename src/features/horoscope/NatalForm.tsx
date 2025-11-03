import { useState, type FormEvent } from 'react';
import { useCreateNatal } from './hooks/useCreateNatal';

/**
 * Props pour le composant NatalForm
 */
export interface NatalFormProps {
  /** Callback appelé après création réussie avec le chartId */
  onSuccess?: (chartId: string) => void;
}

/**
 * Formulaire pour créer un thème natal
 * Validation stricte côté client (bornes lat/lng, required)
 * Timezone auto-détecté
 * Double-submit bloqué
 * A11y complet
 */
export function NatalForm({ onSuccess }: NatalFormProps): JSX.Element {
  const { createNatal, isPending, fieldErrors } = useCreateNatal();

  // State pour les champs du formulaire
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [latitude, setLatitude] = useState<number | ''>('');
  const [longitude, setLongitude] = useState<number | ''>('');
  const [locationName, setLocationName] = useState('');

  // Timezone auto-détecté
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

  // Validation côté client
  const [errors, setErrors] = useState<{
    date?: string;
    time?: string;
    latitude?: string;
    longitude?: string;
  }>({});

  // Vérifier si le formulaire est valide
  const isFormValid =
    date &&
    time &&
    latitude !== '' &&
    longitude !== '' &&
    typeof latitude === 'number' &&
    typeof longitude === 'number' &&
    latitude >= -90 &&
    latitude <= 90 &&
    longitude >= -180 &&
    longitude <= 180 &&
    Object.keys(errors).length === 0;

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (pending || !isFormValid) return;

    // Reset errors
    setErrors({});

    // Validation finale
    const clientErrors: {
      date?: string;
      time?: string;
      latitude?: string;
      longitude?: string;
    } = {};

    if (!date) {
      clientErrors.date = 'Date requise';
    }
    if (!time) {
      clientErrors.time = 'Heure requise';
    }
    if (typeof latitude !== 'number') {
      clientErrors.latitude = 'Latitude requise';
    } else if (latitude < -90 || latitude > 90) {
      clientErrors.latitude = 'Latitude doit être entre -90 et 90';
    }
    if (typeof longitude !== 'number') {
      clientErrors.longitude = 'Longitude requise';
    } else if (longitude < -180 || longitude > 180) {
      clientErrors.longitude = 'Longitude doit être entre -180 et 180';
    }

    if (Object.keys(clientErrors).length > 0) {
      setErrors(clientErrors);
      return;
    }

    // Fusionner erreurs serveur et client
    const allErrors = { ...clientErrors, ...fieldErrors };
    if (Object.keys(allErrors).length > 0) {
      setErrors(allErrors);
      return;
    }

    try {
      const chartId = await createNatal({
        date,
        time,
        latitude,
        longitude,
        timezone,
        name: locationName.trim() || undefined,
      });

      // Success géré dans le hook
      if (onSuccess && chartId) {
        onSuccess(chartId);
      }
    } catch {
      // Erreurs déjà gérées dans le hook
    }
  };

  // Variable pending combinée
  const pending = isPending;

  return (
    <div style={{ marginBottom: '2rem' }}>
      <h2>Créer un thème natal</h2>
      <form
        onSubmit={(e) => {
          void handleSubmit(e);
        }}
        noValidate
      >
        {/* Date */}
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="date">
            Date de naissance <span aria-label="requis">*</span>
          </label>
          <input
            type="date"
            id="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            aria-invalid={errors.date ? 'true' : undefined}
            aria-describedby={errors.date ? 'date-error' : undefined}
            required
          />
          {errors.date && (
            <span id="date-error" role="alert" aria-live="polite">
              {errors.date}
            </span>
          )}
        </div>

        {/* Heure */}
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="time">
            Heure de naissance <span aria-label="requis">*</span>
          </label>
          <input
            type="time"
            id="time"
            value={time}
            onChange={(e) => setTime(e.target.value)}
            aria-invalid={errors.time ? 'true' : undefined}
            aria-describedby={errors.time ? 'time-error' : undefined}
            required
          />
          {errors.time && (
            <span id="time-error" role="alert" aria-live="polite">
              {errors.time}
            </span>
          )}
        </div>

        {/* Lat/Long */}
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <div style={{ flex: 1 }}>
            <label htmlFor="latitude">
              Latitude <span aria-label="requis">*</span>
              <br />
              <small>Entre -90 et 90</small>
            </label>
            <input
              type="number"
              id="latitude"
              min="-90"
              max="90"
              step="any"
              value={latitude}
              onChange={(e) => {
                const val = e.target.value;
                setLatitude(val === '' ? '' : parseFloat(val));
              }}
              aria-invalid={errors.latitude ? 'true' : undefined}
              aria-describedby={errors.latitude ? 'latitude-error' : undefined}
              required
            />
            {errors.latitude && (
              <span id="latitude-error" role="alert" aria-live="polite">
                {errors.latitude}
              </span>
            )}
          </div>

          <div style={{ flex: 1 }}>
            <label htmlFor="longitude">
              Longitude <span aria-label="requis">*</span>
              <br />
              <small>Entre -180 et 180</small>
            </label>
            <input
              type="number"
              id="longitude"
              min="-180"
              max="180"
              step="any"
              value={longitude}
              onChange={(e) => {
                const val = e.target.value;
                setLongitude(val === '' ? '' : parseFloat(val));
              }}
              aria-invalid={errors.longitude ? 'true' : undefined}
              aria-describedby={
                errors.longitude ? 'longitude-error' : undefined
              }
              required
            />
            {errors.longitude && (
              <span id="longitude-error" role="alert" aria-live="polite">
                {errors.longitude}
              </span>
            )}
          </div>
        </div>

        {/* Lieu (optionnel) */}
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="location">Lieu (optionnel)</label>
          <input
            type="text"
            id="location"
            value={locationName}
            onChange={(e) => setLocationName(e.target.value)}
          />
        </div>

        {/* Timezone (auto-détecté, lecture seule) */}
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="timezone">Fuseau horaire</label>
          <input
            type="text"
            id="timezone"
            value={timezone}
            readOnly
            style={{ backgroundColor: '#f5f5f5', cursor: 'not-allowed' }}
          />
        </div>

        {/* Bouton submit */}
        <button type="submit" disabled={!isFormValid || pending}>
          {pending ? 'Création...' : 'Créer le thème natal'}
        </button>
      </form>
    </div>
  );
}
