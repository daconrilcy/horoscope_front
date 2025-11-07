/**
 * EventBus léger pour découpler le client HTTP de l'UI
 * Système pub/sub simple pour émettre et écouter des événements
 */

type EventCallback = (payload?: unknown) => void;

type EventType =
  | 'auth:unauthorized'
  | 'paywall:plan'
  | 'paywall:rate'
  | 'api:request';

class EventBus {
  private listeners: Map<EventType, Set<EventCallback>> = new Map();

  /**
   * Souscrit à un événement
   */
  on(event: EventType, callback: EventCallback): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);

    // Retourne une fonction de désabonnement
    return () => this.off(event, callback);
  }

  /**
   * Se désabonne d'un événement
   */
  off(event: EventType, callback: EventCallback): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.delete(callback);
      if (callbacks.size === 0) {
        this.listeners.delete(event);
      }
    }
  }

  /**
   * Émet un événement avec un payload optionnel
   */
  emit(event: EventType, payload?: unknown): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach((callback) => {
        try {
          callback(payload);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
    }
  }

  /**
   * Supprime tous les listeners (utile pour les tests)
   */
  clear(): void {
    this.listeners.clear();
  }
}

export const eventBus = new EventBus();
