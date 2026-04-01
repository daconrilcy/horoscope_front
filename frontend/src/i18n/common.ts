import { APP_NAME } from "@utils/constants"

import type { AstrologyLang } from "./astrology"

export interface CommonTranslation {
  header: {
    appTitle: string
    logout: string
    defaultRole: string
    openMenu: string
    closeMenu: string
    toggleTheme: string
    openUserMenu: string
  }
  userMenu: {
    editAccount: string
    astrologers: string
    help: string
    logout: string
    settings: string
  }
  heroCard: {
    readShort: string
    readDetailed: string
    ariaReadShort: string
    ariaReadDetailed: string
  }
  actions: {
    close: string
    cancel: string
    confirm: string
    retry: string
    back: string
    next: string
    delete: string
    save: string
  }
  states: {
    loading: string
    error: string
    empty: string
    noData: string
  }
}

const translations: Record<AstrologyLang, CommonTranslation> = {
  fr: {
    header: {
      appTitle: APP_NAME,
      logout: "Se déconnecter",
      defaultRole: "Utilisateur",
      openMenu: "Ouvrir le menu",
      closeMenu: "Fermer le menu",
      toggleTheme: "Changer le thème",
      openUserMenu: "Menu utilisateur",
    },
    userMenu: {
      editAccount: "Modifier mon compte",
      astrologers: "Voir les astrologues",
      help: "Aide & Support",
      logout: "Se déconnecter",
      settings: "Paramètres",
    },
    heroCard: {
      readShort: "Lire en 2 min",
      readDetailed: "Version détaillée",
      ariaReadShort: "Lire l'horoscope complet en 2 minutes",
      ariaReadDetailed: "Voir la version détaillée de l'horoscope",
    },
    actions: {
      close: "Fermer",
      cancel: "Annuler",
      confirm: "Confirmer",
      retry: "Réessayer",
      back: "Retour",
      next: "Suivant",
      delete: "Supprimer",
      save: "Enregistrer",
    },
    states: {
      loading: "Chargement...",
      error: "Erreur",
      empty: "Aucun résultat",
      noData: "Aucune donnée disponible",
    },
  },
  en: {
    header: {
      appTitle: APP_NAME,
      logout: "Log out",
      defaultRole: "User",
      openMenu: "Open menu",
      closeMenu: "Close menu",
      toggleTheme: "Toggle theme",
      openUserMenu: "User menu",
    },
    userMenu: {
      editAccount: "Edit account",
      astrologers: "View astrologers",
      help: "Help & Support",
      logout: "Log out",
      settings: "Settings",
    },
    heroCard: {
      readShort: "2 min read",
      readDetailed: "Detailed version",
      ariaReadShort: "Read full horoscope in 2 minutes",
      ariaReadDetailed: "View detailed version of the horoscope",
    },
    actions: {
      close: "Close",
      cancel: "Cancel",
      confirm: "Confirm",
      retry: "Retry",
      back: "Back",
      next: "Next",
      delete: "Delete",
      save: "Save",
    },
    states: {
      loading: "Loading...",
      error: "Error",
      empty: "No results",
      noData: "No data available",
    },
  },
  es: {
    header: {
      appTitle: APP_NAME,
      logout: "Cerrar sesión",
      defaultRole: "Usuario",
      openMenu: "Abrir menú",
      closeMenu: "Cerrar menú",
      toggleTheme: "Cambiar tema",
      openUserMenu: "Menú de usuario",
    },
    userMenu: {
      editAccount: "Editar cuenta",
      astrologers: "Ver astrólogos",
      help: "Ayuda y Soporte",
      logout: "Cerrar sesión",
      settings: "Configuración",
    },
    heroCard: {
      readShort: "Lectura 2 min",
      readDetailed: "Versión detallada",
      ariaReadShort: "Leer horóscopo completo en 2 minutos",
      ariaReadDetailed: "Ver versión detallada del horóscopo",
    },
    actions: {
      close: "Cerrar",
      cancel: "Cancelar",
      confirm: "Confirmar",
      retry: "Reintentar",
      back: "Atrás",
      next: "Siguiente",
      delete: "Eliminar",
      save: "Guardar",
    },
    states: {
      loading: "Cargando...",
      error: "Error",
      empty: "Sin resultados",
      noData: "No hay datos disponibles",
    },
  },
}

export function commonTranslations(lang: AstrologyLang = "fr"): CommonTranslation {
  return translations[lang] ?? translations.fr
}
