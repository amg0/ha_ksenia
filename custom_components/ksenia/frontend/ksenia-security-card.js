/**
 * Ksenia Lares Security Card - high-density Lovelace card.
 *
 * Shows partition status and zone motion sensors in a compact,
 * modern dark-themed layout suitable for wall tablets and mobile.
 *
 * Configuration (yaml):
 *   - type: custom/ksenia-security-card
 *     title: Security (optional)
 *     partitions:
 *       - binary_sensor.partition_main
 *     zones:
 *       - binary_sensor.zone_front_door
 *       - binary_sensor.zone_living_room
 *     show_bypass: true          (default: false)
 *     compact: true              (default: true)
 */

import { LitElement } from "lit";
import { customElement, property } from "lit/decorators.js";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PARTITION_ICONS = {
  DISARMED: "hass:shield-open",
  ARMED_AWAY: "hass:shield-lock",
  ARMED_HOME: "hass:shield-home",
  ARMED_NIGHT: "hass:shield-moon",
  ARMED_VACATION: "hass:shield-check",
  PENDING: "hass:shield-alert",
  TRIGGERED: "hass:shield-bash",
  UNKNOWN: "hass:shield-outline",
};

const ZONE_ICONS = {
  on: "hass:motion-sensor",
  off: "hass:motion-sensor-off",
};

const PARTITION_COLORS = {
  DISARMED: "#4caf50",
  ARMED_AWAY: "#2196f3",
  ARMED_HOME: "#ff9800",
  ARMED_NIGHT: "#9c27b0",
  ARMED_VACATION: "#607d8b",
  PENDING: "#ffc107",
  TRIGGERED: "#f44336",
  UNKNOWN: "#9e9e9e",
};

const ZONE_COLORS_TRIGGERED = "#f44336";
const ZONE_COLORS_NORMAL = "#4caf50";
const ZONE_COLORS_BYPASS = "#ff9800";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatPartitionStatus(status) {
  const labels = {
    DISARMED: "Disarmed",
    ARMED_AWAY: "Away",
    ARMED_HOME: "Home",
    ARMED_NIGHT: "Night",
    ARMED_VACATION: "Vacation",
    PENDING: "Pending",
    TRIGGERED: "Triggered",
    UNKNOWN: "Unknown",
  };
  return labels[status] ?? status;
}

function formatZoneName(entityId) {
  const parts = entityId.split(".");
  if (parts.length < 2) return entityId;
  return parts[1].replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

// ---------------------------------------------------------------------------
// Card element
// ---------------------------------------------------------------------------

@customElement("ksenia-security-card")
class KseniaSecurityCard extends LitElement {
  // Config
  config = {};

  // Internal state
  _partitions = [];
  _zones = [];

  // -----------------------------------------------------------------------
  // Lifecycle
  // -----------------------------------------------------------------------

  setConfig(config) {
    this.config = {
      ...config,
      show_bypass: config.show_bypass ?? false,
      compact: config.compact !== false,
    };
  }

  updated(changedProps) {
    if (!this.hass || !this.config) return;

    // Re-compute partition states
    const newPartitions = [];
    for (const entityId of this.config.partitions ?? []) {
      const stateObj = this.hass.states[entityId];
      if (!stateObj) continue;
      const isDisarmed = stateObj.state === "on";
      const status = stateObj.attributes?.partition_status ?? "UNKNOWN";
      newPartitions.push({ entityId, isDisarmed, status });
    }

    // Re-compute zone states
    const newZones = [];
    for (const entityId of this.config.zones ?? []) {
      const stateObj = this.hass.states[entityId];
      if (!stateObj) continue;
      const triggered = stateObj.state === "on";
      const bypassed = stateObj.attributes?.bypass === "BYPASS" || false;
      newZones.push({
        entityId,
        triggered,
        bypassed,
        name: this.config.compact ? formatZoneName(entityId) : "",
      });
    }

    this._partitions = newPartitions;
    this._zones = newZones;
  }

  // -----------------------------------------------------------------------
  // Render helpers (LitElement uses html tagged template literals)
  // -----------------------------------------------------------------------

  render() {
    if (!this.hass) return "";

    const title = this.config.title ?? "Security";
    const showBypass = this.config.show_bypass ?? false;
    const compact = this.config.compact !== false;

    return `
      <div class="card ${compact ? "compact" : ""}">
        <div class="card-header">${title}</div>
        <div class="content">
          ${this._renderPartitions()} ${this._renderZones(showBypass)}
        </div>
      </div>
    `;
  }

  _renderPartitions() {
    if (this._partitions.length === 0) return "";

    return this._partitions.map((p) => this._renderPartition(p)).join("");
  }

  _renderPartition(p) {
    const color = PARTITION_COLORS[p.status] ?? PARTITION_COLORS.UNKNOWN;
    const icon = PARTITION_ICONS[p.status] ?? PARTITION_ICONS.UNKNOWN;
    const label = formatPartitionStatus(p.status);
    const entityId = p.entityId.split(".").pop() ?? "";

    return `
      <div class="partition" data-action="toggle-partition" data-entity="${p.entityId}" data-disarmed="${p.isDisarmed}">
        <div class="partition-indicator" style="background:${color}"></div>
        <div class="partition-info">
          <span class="partition-label">${label}</span>
          <span class="partition-name">${entityId.replace(/_/g, " ")}</span>
        </div>
        <ha-icon icon="${icon}" class="partition-icon"></ha-icon>
      </div>
    `;
  }

  _renderZones(showBypass) {
    if (this._zones.length === 0) return "";

    return this._zones.map((z) => this._renderZone(z, showBypass)).join("");
  }

  _renderZone(z, showBypass) {
    let color = ZONE_COLORS_NORMAL;
    if (z.bypassed) color = ZONE_COLORS_BYPASS;
    else if (z.triggered) color = ZONE_COLORS_TRIGGERED;

    const icon = z.triggered ? ZONE_ICONS.on : ZONE_ICONS.off;
    const name = this.config.compact ? "" : formatZoneName(z.entityId);
    const bypassBadge = showBypass && z.bypassed ? '<span class="zone-bypass-badge">BY</span>' : "";

    return `
      <div class="zone ${z.triggered ? "triggered" : ""} ${z.bypassed ? "bypassed" : ""}" style="--zone-color: ${color}">
        <ha-icon icon="${icon}" class="zone-icon"></ha-icon>
        ${name ? `<span class="zone-name">${name}</span>` : ""}
        ${bypassBadge}
      </div>
    `;
  }

  // -----------------------------------------------------------------------
  // Actions
  // -----------------------------------------------------------------------

  _togglePartition(entityId, isDisarmed) {
    if (!this.hass) return;
    this.hass.callService("alarm_control_panel", isDisarmed ? "alarm_arm_away" : "alarm_disarm", {
      entity_id: entityId,
    });
  }

  // -----------------------------------------------------------------------
  // Styles
  // -----------------------------------------------------------------------

  static get styles() {
    return `
      :host {
        --ksenia-primary: #1a73e8;
        --ksenia-bg: #1e1e2e;
        --ksenia-surface: #2a2a3e;
        --ksenia-text: #e0e0e0;
        --ksenia-text-secondary: #9e9e9e;
        --ksenia-border: rgba(255, 255, 255, 0.08);
        --ksenia-radius: 12px;
        --ksenia-transition: 200ms ease;

        display: block;
      }

      .card {
        background: var(--ksenia-bg);
        border-radius: var(--ksenia-radius);
        overflow: hidden;
        font-family: "Roboto", "Segoe UI", system-ui, sans-serif;
        color: var(--ksenia-text);
        transition: box-shadow var(--ksenia-transition);
      }

      .card.compact {
        --mdc-typography-button-font-size: 12px;
      }

      .card-header {
        padding: 16px 20px 8px;
        font-size: 18px;
        font-weight: 600;
        letter-spacing: -0.3px;
        color: var(--ksenia-text);
      }

      .content {
        padding: 4px 12px 12px;
      }

      /* ---- Partitions ---- */
      .section.partitions {
        display: flex;
        gap: 8px;
        margin-bottom: 12px;
        flex-wrap: wrap;
      }

      .partition {
        flex: 1 1 0;
        min-width: 140px;
        background: var(--ksenia-surface);
        border-radius: 10px;
        padding: 12px 14px;
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
        transition: transform var(--ksenia-transition), box-shadow var(--ksenia-transition);
        border: 1px solid var(--ksenia-border);
      }

      .partition:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
      }

      .partition-indicator {
        width: 8px;
        height: 32px;
        border-radius: 4px;
        flex-shrink: 0;
      }

      .partition-info {
        flex: 1 1 auto;
        min-width: 0;
        display: flex;
        flex-direction: column;
        gap: 2px;
      }

      .partition-label {
        font-size: 13px;
        font-weight: 600;
        color: var(--ksenia-text);
        line-height: 1.2;
      }

      .partition-name {
        font-size: 11px;
        color: var(--ksenia-text-secondary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .partition-icon {
        flex-shrink: 0;
        color: var(--ksenia-text-secondary);
      }

      .partition-icon ha-svg-icon {
        font-size: 24px;
      }

      /* ---- Zones ---- */
      .section.zones {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
        gap: 6px;
      }

      .zone {
        background: var(--ksenia-surface);
        border-radius: 8px;
        padding: 10px 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        border: 1.5px solid var(--zone-color, var(--ksenia-border));
        transition: background var(--ksenia-transition), border-color var(--ksenia-transition);
        position: relative;
      }

      .zone.triggered {
        background: color-mix(in srgb, var(--zone-color) 12%, transparent);
        animation: pulse-zone 2s ease-in-out infinite;
      }

      .zone.bypassed {
        border-style: dashed;
      }

      @keyframes pulse-zone {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; }
      }

      .zone-icon {
        color: var(--zone-color);
        font-size: 20px;
        flex-shrink: 0;
      }

      .zone-icon ha-svg-icon {
        font-size: 20px;
      }

      .zone-name {
        font-size: 10px;
        color: var(--ksenia-text-secondary);
        text-align: center;
        line-height: 1.2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .zone-bypass-badge {
        position: absolute;
        top: 2px;
        right: 4px;
        font-size: 8px;
        font-weight: 700;
        color: #ff9800;
        background: rgba(255, 152, 0, 0.15);
        padding: 1px 3px;
        border-radius: 3px;
      }

      /* ---- Compact mode ---- */
      .card.compact .card-header {
        font-size: 16px;
        padding: 12px 16px 4px;
      }

      .card.compact .content {
        padding: 2px 8px 8px;
      }

      .card.compact .partition {
        padding: 8px 10px;
        min-width: 110px;
      }

      .card.compact .partition-label {
        font-size: 12px;
      }

      .card.compact .partition-name {
        font-size: 10px;
      }

      .card.compact .section.zones {
        grid-template-columns: repeat(auto-fill, minmax(64px, 1fr));
        gap: 4px;
      }

      /* ---- Responsive ---- */
      @media (max-width: 400px) {
        .section.partitions {
          flex-direction: column;
        }
        .partition {
          min-width: unset;
        }
      }
    `;
  }
}

// ---------------------------------------------------------------------------
// Register card with Home Assistant
// ---------------------------------------------------------------------------

if (customElements.get("ksenia-security-card") === undefined) {
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "ksenia-security-card",
    name: "Ksenia Security",
    preview: true,
    description: "High-density security card showing partition and zone status for Ksenia Lares alarm systems.",
  });
}

export default KseniaSecurityCard;
