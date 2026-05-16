import type { AstrologyLang } from "./astrology"

export type BirthProfileValidation = {
  dateRequired: string
  dateFormat: string
  dateInvalid: string
  dateFuture: string
  timeFormat: string
  timezoneRequired: string
  timezoneFormat: string
  cityRequired: string
  countryRequired: string
}

type BirthProfileTranslations = {
  title: string
  loading: string
  loadError: string
  retry: string
  labels: {
    birthDate: string
    birthTime: string
    unknownTime: string
    birthCity: string
    birthCountry: string
    birthTimezone: string
    birthInfo: string
    currentLocation: string
    currentCity: string
    currentCountry: string
    locationHelp: string
    allowGeolocation: string
    detectNow: string
    detecting: string
    locationDetected: string
    noLocation: string
    manualLocationHelp: string
  }
  buttons: {
    save: string
    saving: string
    generate: string
    /** Template string with `{timeout}` placeholder — use `.replace("{timeout}", value)` */
    generating: string
  }
  status: {
    saveSuccess: string
    generationSection: string
  }
  errors: {
    generationTimeout: string
    generationUnavailable: string
    generationInvalidData: string
    generationGeneric: string
    saveNetwork: string
    saveInvalidData: string
    locationFailed: string
    geolocationUnavailable: string
    geolocationDenied: string
  }
  validation: BirthProfileValidation
}

export type BirthProfileTranslation = BirthProfileTranslations;
export const birthProfileTranslations: Record<AstrologyLang, BirthProfileTranslations> = {
  fr: {
    title: "Mon profil natal",
    loading: "Chargement de votre profil natal...",
    loadError: "Impossible de charger votre profil natal. Veuillez réessayer plus tard.",
    retry: "Réessayer",
    labels: {
      birthDate: "Date de naissance (YYYY-MM-DD)",
      birthTime: "Heure de naissance (HH:MM)",
      unknownTime: "Heure inconnue",
      birthCity: "Ville de naissance",
      birthCountry: "Pays de naissance",
      birthTimezone: "Fuseau horaire",
      birthInfo: "Informations de naissance",
      currentLocation: "Localisation actuelle",
      currentCity: "Ville actuelle",
      currentCountry: "Pays actuel",
      locationHelp: "La localisation actuelle permet de personnaliser vos guidances avec les énergies du lieu où vous vous trouvez.",
      allowGeolocation: "Autoriser la géolocalisation pour personnaliser mes guidances",
      detectNow: "Me localiser maintenant",
      detecting: "Détection...",
      locationDetected: "Lieu détecté",
      noLocation: "Aucun lieu détecté",
      manualLocationHelp: "Si vous refusez la geolocalisation ou si elle echoue, indiquez votre lieu actuel pour ancrer les interpretations dans votre ciel local.",
    },
    buttons: {
      save: "Sauvegarder",
      saving: "Sauvegarde en cours...",
      generate: "Générer mon thème astral",
      generating: "Génération en cours (max {timeout})...",
    },
    status: {
      saveSuccess: "Profil natal sauvegardé.",
      generationSection: "Génération du thème astral",
    },
    errors: {
      generationTimeout: "La génération a pris trop de temps, veuillez réessayer.",
      generationUnavailable: "Le service de génération est temporairement indisponible.",
      generationInvalidData:
        "Vos données de naissance sont invalides ou incomplètes. Veuillez vérifier votre profil natal.",
      generationGeneric: "Une erreur est survenue. Veuillez réessayer.",
      saveNetwork: "Erreur lors de la sauvegarde. Veuillez réessayer.",
      saveInvalidData: "Données invalides. Vérifiez les champs.",
      locationFailed: "La détection de la localisation a échoué.",
      geolocationUnavailable: "La geolocalisation n'est pas disponible dans ce navigateur ou cette page n'est pas securisee.",
      geolocationDenied: "L'autorisation de geolocalisation a ete refusee.",
    },
    validation: {
      dateRequired: "La date de naissance est indispensable pour calculer votre thème natal.",
      dateFormat: "Format YYYY-MM-DD requis (ex: 1990-01-15)",
      dateInvalid: "Date invalide",
      dateFuture: "La date de naissance ne peut pas être dans le futur",
      timeFormat: "Format HH:MM(:SS) requis (ex: 10:30)",
      timezoneRequired: "Le fuseau horaire est requis",
      timezoneFormat:
        "Format IANA requis (ex: Europe/Paris, UTC ou America/Argentina/Buenos_Aires)",
      cityRequired: "La ville de naissance est requise",
      countryRequired: "Le pays de naissance est requis",
    },
  },
  en: {
    title: "My natal profile",
    loading: "Loading your natal profile...",
    loadError: "Unable to load your natal profile. Please try again later.",
    retry: "Retry",
    labels: {
      birthDate: "Date of birth (YYYY-MM-DD)",
      birthTime: "Time of birth (HH:MM)",
      unknownTime: "Unknown time",
      birthCity: "City of birth",
      birthCountry: "Country of birth",
      birthTimezone: "Time zone",
      birthInfo: "Birth information",
      currentLocation: "Current location",
      currentCity: "Current city",
      currentCountry: "Current country",
      locationHelp: "Current location allows personalizing your guidance with the energies of where you are.",
      allowGeolocation: "Allow geolocation to personalize my guidance",
      detectNow: "Locate me now",
      detecting: "Detecting...",
      locationDetected: "Location detected",
      noLocation: "No location detected",
      manualLocationHelp: "If you refuse geolocation or it fails, enter your current location to anchor interpretations in your local sky.",
    },
    buttons: {
      save: "Save",
      saving: "Saving...",
      generate: "Generate my natal chart",
      generating: "Generating (max {timeout})...",
    },
    status: {
      saveSuccess: "Natal profile saved.",
      generationSection: "Natal chart generation",
    },
    errors: {
      generationTimeout: "Generation took too long, please try again.",
      generationUnavailable: "The generation service is temporarily unavailable.",
      generationInvalidData:
        "Your birth data is invalid or incomplete. Please check your natal profile.",
      generationGeneric: "An error occurred. Please try again.",
      saveNetwork: "Error while saving. Please try again.",
      saveInvalidData: "Invalid data. Check the fields.",
      locationFailed: "Location detection failed.",
      geolocationUnavailable: "Geolocation is unavailable in this browser or the page is not secure.",
      geolocationDenied: "Geolocation permission was denied.",
    },
    validation: {
      dateRequired: "Date of birth is required to calculate your natal chart.",
      dateFormat: "YYYY-MM-DD format required (e.g. 1990-01-15)",
      dateInvalid: "Invalid date",
      dateFuture: "Date of birth cannot be in the future",
      timeFormat: "HH:MM(:SS) format required (e.g. 10:30)",
      timezoneRequired: "Time zone is required",
      timezoneFormat:
        "IANA format required (e.g. Europe/Paris, UTC or America/Argentina/Buenos_Aires)",
      cityRequired: "City of birth is required",
      countryRequired: "Country of birth is required",
    },
  },
  es: {
    title: "Mi perfil natal",
    loading: "Cargando tu perfil natal...",
    loadError: "No se pudo cargar tu perfil natal. Por favor, inténtalo más tarde.",
    retry: "Reintentar",
    labels: {
      birthDate: "Fecha de nacimiento (YYYY-MM-DD)",
      birthTime: "Hora de nacimiento (HH:MM)",
      unknownTime: "Hora desconocida",
      birthCity: "Ciudad de nacimiento",
      birthCountry: "País de nacimiento",
      birthTimezone: "Zona horaria",
      birthInfo: "Información de nacimiento",
      currentLocation: "Ubicación actual",
      currentCity: "Ciudad actual",
      currentCountry: "País actual",
      locationHelp: "La ubicación actual permite personalizar tus orientaciones con las energías del lugar donde te encuentras.",
      allowGeolocation: "Permitir geolocalización para personalizar mis orientaciones",
      detectNow: "Localizarme ahora",
      detecting: "Detectando...",
      locationDetected: "Ubicación detectada",
      noLocation: "No se detectó ubicación",
      manualLocationHelp: "Si rechazas la geolocalización o falla, indica tu ubicación actual para anclar las interpretaciones en tu cielo local.",
      },
    buttons: {
      save: "Guardar",
      saving: "Guardando...",
      generate: "Generar mi carta natal",
      generating: "Generando (máx {timeout})...",
    },
    status: {
      saveSuccess: "Perfil natal guardado.",
      generationSection: "Generación de la carta natal",
    },
    errors: {
      generationTimeout: "La generación tardó demasiado, por favor inténtalo de nuevo.",
      generationUnavailable: "El servicio de generación no está disponible temporalmente.",
      generationInvalidData:
        "Tus datos de nacimiento son inválidos o incompletos. Por favor, verifica tu perfil natal.",
      generationGeneric: "Ocurrió un error. Por favor, inténtalo de nuevo.",
      saveNetwork: "Error al guardar. Por favor, inténtalo de nuevo.",
      saveInvalidData: "Datos inválidos. Verifica los campos.",
      locationFailed: "La detección de la ubicación falló.",
      geolocationUnavailable: "La geolocalización no está disponible en este navegador o la página no es segura.",
      geolocationDenied: "Se rechazó el permiso de geolocalización.",
      },
    validation: {
      dateRequired: "La fecha de nacimiento es indispensable para calcular tu carta natal.",
      dateFormat: "Formato YYYY-MM-DD requerido (ej: 1990-01-15)",
      dateInvalid: "Fecha inválida",
      dateFuture: "La fecha de nacimiento no puede ser en el futuro",
      timeFormat: "Formato HH:MM(:SS) requerido (ej: 10:30)",
      timezoneRequired: "La zona horaria es requerida",
      timezoneFormat:
        "Formato IANA requerido (ej: Europe/Paris, UTC o America/Argentina/Buenos_Aires)",
      cityRequired: "La ciudad de nacimiento es requerida",
      countryRequired: "El país de nacimiento es requerido",
    },
  },
  de: {
    title: "Mein Geburtsprofil",
    loading: "Ihr Geburtsprofil wird geladen...",
    loadError: "Ihr Geburtsprofil konnte nicht geladen werden. Bitte versuchen Sie es später erneut.",
    retry: "Erneut versuchen",
    labels: {
      birthDate: "Geburtsdatum (YYYY-MM-DD)",
      birthTime: "Geburtszeit (HH:MM)",
      unknownTime: "Zeit unbekannt",
      birthCity: "Geburtsstadt",
      birthCountry: "Geburtsland",
      birthTimezone: "Zeitzone",
      birthInfo: "Geburtsinformationen",
      currentLocation: "Aktueller Standort",
      currentCity: "Aktuelle Stadt",
      currentCountry: "Aktuelles Land",
      locationHelp: "Der aktuelle Standort hilft, Ihre Hinweise mit den Energien Ihres Aufenthaltsortes zu personalisieren.",
      allowGeolocation: "Geolokalisierung erlauben, um meine Hinweise zu personalisieren",
      detectNow: "Meinen Standort erkennen",
      detecting: "Erkennung läuft...",
      locationDetected: "Standort erkannt",
      noLocation: "Kein Standort erkannt",
      manualLocationHelp: "Wenn Sie die Geolokalisierung ablehnen oder sie fehlschlägt, geben Sie Ihren aktuellen Standort an, um die Deutungen an Ihrem lokalen Himmel zu verankern.",
    },
    buttons: {
      save: "Speichern",
      saving: "Wird gespeichert...",
      generate: "Mein Geburtshoroskop erstellen",
      generating: "Erstellung läuft (max. {timeout})...",
    },
    status: {
      saveSuccess: "Geburtsprofil gespeichert.",
      generationSection: "Erstellung des Geburtshoroskops",
    },
    errors: {
      generationTimeout: "Die Erstellung hat zu lange gedauert. Bitte versuchen Sie es erneut.",
      generationUnavailable: "Der Erstellungsdienst ist vorübergehend nicht verfügbar.",
      generationInvalidData:
        "Ihre Geburtsdaten sind ungültig oder unvollständig. Bitte prüfen Sie Ihr Geburtsprofil.",
      generationGeneric: "Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.",
      saveNetwork: "Fehler beim Speichern. Bitte versuchen Sie es erneut.",
      saveInvalidData: "Ungültige Daten. Prüfen Sie die Felder.",
      locationFailed: "Die Standorterkennung ist fehlgeschlagen.",
      geolocationUnavailable: "Geolokalisierung ist in diesem Browser nicht verfügbar oder die Seite ist nicht sicher.",
      geolocationDenied: "Die Berechtigung zur Geolokalisierung wurde verweigert.",
    },
    validation: {
      dateRequired: "Das Geburtsdatum ist erforderlich, um Ihr Geburtshoroskop zu berechnen.",
      dateFormat: "Format YYYY-MM-DD erforderlich (z. B. 1990-01-15)",
      dateInvalid: "Ungültiges Datum",
      dateFuture: "Das Geburtsdatum darf nicht in der Zukunft liegen",
      timeFormat: "Format HH:MM(:SS) erforderlich (z. B. 10:30)",
      timezoneRequired: "Die Zeitzone ist erforderlich",
      timezoneFormat:
        "IANA-Format erforderlich (z. B. Europe/Paris, UTC oder America/Argentina/Buenos_Aires)",
      cityRequired: "Die Geburtsstadt ist erforderlich",
      countryRequired: "Das Geburtsland ist erforderlich",
    },
  },
}
