/**
 * Types partagés pour le client HTTP et les stores
 */

export type PaywallReason = 'plan' | 'rate';

export interface PaywallPayload {
  reason?: PaywallReason;
  upgradeUrl?: string;
  feature?: string;
  retry_after?: number;
}
