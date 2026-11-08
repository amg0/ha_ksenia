/**
 * Ksenia Lares Lovelace Card
 * A compact security dashboard card for the Ksenia Lares Home Assistant integration.
 */

const LitElement = Object.getPrototypeOf(
  customElements.get("hui-masonry-view") ||
    customElements.get("ha-panel-lovelace") ||
    customElements.get("hui-view") ||
    HTMLElement
);
const { html, css } = LitElement.prototype;

const translations = {
  en: {
    editor: {
      title: "Card Title (Optional)",
      entity: "Ksenia Panel / Connectivity Entity (Optional)",
      zone_columns: "Number of columns for zones (default 4)",
      partition_columns: "Number of columns for partitions (default 4)",
      button_columns: "Number of columns for buttons (default 4)",
      confirm_bypass: "Confirm before toggling zone bypass",
    },
    status: {
      online: "Online",
      offline: "Offline",
      no_sensor: "No sensor",
      unavailable: "Unavailable",
    },
    sections: {
      partitions: "Partitions",
      buttons: "Scenarios",
      zones: "Zones",
    },
    zone: {
      open: "Open",
      closed: "Closed",
      smoke: "Smoke!",
      clear: "Clear",
      motion: "Motion",
      no_motion: "No motion",
      lost: "Lost",
      bypass: "bypass",
      confirm_bypass: "Toggle bypass for zone",
    },
    partition: {
      disarmed: "Disarmed",
      armed: "Armed",
      armed_immediate: "Armed Immediate",
      exit: "Exit",
      prealarm: "Prealarm",
      alarm: "Alarm",
      unknown: "Unknown",
    },
  },
  fr: {
    editor: {
      title: "Titre de la carte (Optionnel)",
      entity: "Capteur de connectivite Ksenia (Optionnel)",
      zone_columns: "Nombre de colonnes pour les zones (défaut 4)",
      partition_columns: "Nombre de colonnes pour les partitions (défaut 4)",
      button_columns: "Nombre de colonnes pour les scénarios (défaut 4)",
      confirm_bypass: "Confirmer avant d'exclure/inclure une zone",
    },
    status: {
      online: "En ligne",
      offline: "Hors ligne",
      no_sensor: "Aucun capteur",
      unavailable: "Indisponible",
    },
    sections: {
      partitions: "Partitions",
      buttons: "Scénarios",
      zones: "Zones",
    },
    zone: {
      open: "Ouvert",
      closed: "Fermé",
      smoke: "Fumée !",
      clear: "Normal",
      motion: "Détection",
      no_motion: "RAS",
      lost: "Perdu",
      bypass: "isolée",
      confirm_bypass: "Basculer l'exclusion pour la zone",
    },
    partition: {
      disarmed: "Désarmé",
      armed: "Armé",
      armed_immediate: "Armé immédiat",
      exit: "Sortie",
      prealarm: "Pré-alarme",
      alarm: "Alarme",
      unknown: "Inconnu",
    },
  },
};

function getTranslations(hass) {
  const lang = (hass?.language || "en").split("-")[0].toLowerCase();
  return translations[lang] || translations.en;
}

class KseniaLaresCard extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
    };
  }

  static get styles() {
    return css`
      :host {
        display: block;
      }
      ha-card {
        background: var(--ha-card-background, var(--card-background-color, #1e1e2e));
        border-radius: var(--ha-card-border-radius, 12px);
        border: 1px solid var(--ha-card-border-color, var(--divider-color, #313244));
        box-shadow: var(--ha-card-box-shadow, none);
        padding: 16px;
        color: var(--primary-text-color, #cdd6f4);
        font-family: var(--paper-font-body1_-_font-family, sans-serif);
      }
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 10px;
        margin-bottom: 12px;
      }
      .card-header .title {
        font-size: 1em;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
      }
      .card-header .status {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.85em;
        font-weight: 500;
      }
      .status.online {
        color: #2ecc71;
      }
      .status.offline {
        color: #e74c3c;
      }
      .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: currentColor;
        box-shadow: 0 0 6px currentColor;
      }
      .section-title {
        display: flex;
        align-items: center;
        font-size: 0.8em;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: var(--secondary-text-color, #bac2de);
        margin: 12px 0 8px 0;
        font-weight: 600;
      }
      .section-title::after {
        content: "";
        flex: 1;
        height: 1px;
        background-color: var(--divider-color, rgba(255, 255, 255, 0.1));
        margin-left: 12px;
      }
      .grid {
        display: grid;
        gap: 6px;
        margin-bottom: 12px;
      }
      .zone-icon {
        color: var(--paper-item-icon-color, #3498db);
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(52, 152, 219, 0.1);
        padding: 8px;
        border-radius: 50%;
        flex-shrink: 0;
      }
      /* Partition Styles */
      .partition-grid {
        grid-template-columns: repeat(var(--partition-columns, 4), 1fr);
      }
      .partition-item {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(0, 0, 0, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.03);
        padding: 6px;
        border-radius: 6px;
        font-size: 0.85em;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }
      .partition-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        flex-shrink: 0;
      }
      /* Zone Styles */
      .zone-grid {
        grid-template-columns: repeat(var(--zone-columns, 4), 1fr);
      }
      .zone-item {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(0, 0, 0, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.03);
        padding: 6px;
        border-radius: 6px;
        font-size: 0.85em;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        cursor: pointer;
        user-select: none;
        transition: all 0.2s ease-in-out;
      }
      .zone-item:hover {
        background: rgba(0, 0, 0, 0.2);
        border-color: rgba(255, 255, 255, 0.15);
      }
      .zone-item.bypass {
        border-color: rgba(241, 196, 15, 0.3);
        background: rgba(241, 196, 15, 0.05);
      }
      .zone-item.bypass .zone-icon {
        position: relative;
      }
      .zone-item.bypass .zone-icon::after {
        content: "";
        position: absolute;
        top: 50%;
        left: 50%;
        width: 140%;
        height: 2px;
        background-color: rgba(241, 196, 15, 0.7);
        transform: translate(-50%, -50%) rotate(-45deg);
        pointer-events: none;
      }
      /* Button Styles */
      .button-grid {
        grid-template-columns: repeat(var(--button-columns, 4), 1fr);
      }
      .button-item {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 6px;
        border-radius: 6px;
        font-size: 0.85em;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        cursor: pointer;
        user-select: none;
        transition: all 0.2s ease-in-out;
      }
      .button-item:hover {
        background: rgba(0, 0, 0, 0.12);
        border-color: rgba(255, 255, 255, 0.15);
      }
      .button-item:active,
      .zone-item:active {
        transform: scale(0.98);
      }

      /* --- Mobile Responsiveness --- */
      @media screen and (max-width: 600px) {
        ha-card {
          padding: 10px;
        }
        .partition-grid,
        .button-grid,
        .zone-grid {
          grid-template-columns: repeat(2, 1fr) !important;
        }
      }

      @media screen and (max-width: 380px) {
        .partition-grid,
        .button-grid,
        .zone-grid {
          grid-template-columns: 1fr !important;
        }
      }
    `;
  }

  static getStubConfig() {
    return {
      title: "Ksenia Lares Panel",
      entity: "",
      zone_columns: 4,
      partition_columns: 4,
      button_columns: 4,
      confirm_bypass: false,
    };
  }

  shouldUpdate(changedProps) {
    if (changedProps.has("config")) return true;

    if (changedProps.has("hass")) {
      const oldHass = changedProps.get("hass");
      if (!oldHass || oldHass.language !== this.hass.language) return true;

      for (const entityId in this.hass.states) {
        const stateObj = this.hass.states[entityId];
        const oldStateObj = oldHass.states[entityId];

        if (stateObj !== oldStateObj) {
          const attr = stateObj.attributes;
          if (attr && attr.integration && attr.integration.toLowerCase() === "ksenia") {
            return true;
          }
        }
      }
      return false;
    }
    return true;
  }

  render() {
    if (!this.hass || !this.config) return html``;

    const t = getTranslations(this.hass);
    let connectionEntity = null;
    const zoneSensors = [];
    const partitionSensors = [];
    const buttonEntities = [];

    const targetDeviceId = this.config.entity ? this.hass.entities?.[this.config.entity]?.device_id : null;

    for (const entityId in this.hass.states) {
      const stateObj = this.hass.states[entityId];
      const attr = stateObj.attributes;

      if (!attr || !attr.integration || attr.integration.toLowerCase() !== "ksenia") continue;

      if (targetDeviceId) {
        const entityReg = this.hass.entities?.[entityId];
        if (entityReg && entityReg.device_id && entityReg.device_id !== targetDeviceId) {
          continue;
        }
      }

      if (attr.device_class === "connectivity") {
        if (!this.config.entity || entityId === this.config.entity) {
          connectionEntity = stateObj;
        }
      } else if (entityId.startsWith("binary_sensor.")) {
        if (
          attr.device_class === "door" ||
          attr.device_class === "motion" ||
          attr.device_class === "window" ||
          attr.device_class === "smoke"
        ) {
          zoneSensors.push(stateObj);
        } else if (attr.device_class === "lock") {
          partitionSensors.push(stateObj);
        }
      } else if (entityId.startsWith("button.")) {
        buttonEntities.push(stateObj);
      }
    }

    const isOnline = connectionEntity ? connectionEntity.state === "on" : false;
    const statusText = connectionEntity ? (isOnline ? t.status.online : t.status.offline) : t.status.no_sensor;

    const cardTitle =
      this.config.title ||
      (connectionEntity?.attributes.name
        ? connectionEntity.attributes.name
        : connectionEntity?.attributes.friendly_name
          ? connectionEntity.attributes.friendly_name.replace(/ API (connectivity|Connection)/i, "")
          : "Ksenia Lares Panel");

    // Enrich and sort Zones
    const zoneItems = zoneSensors
      .map((sensor) => {
        const attr = sensor.attributes;
        const deviceClass = attr.device_class;
        const zoneStatus = String(attr.zone_status || "").toUpperCase();
        const isUnavailable = sensor.state === "unavailable" || sensor.state === "unknown";
        const stateOn = sensor.state === "on";
        const isBypass = String(attr.bypass || "").toUpperCase() === "BYPASS";

        let label;
        let icon;
        let accentColor = stateOn
          ? deviceClass === "smoke"
            ? "#e6311d"
            : "#ef9b0a"
          : "var(--secondary-text-color)";

        if (isUnavailable) {
          label = t.status.unavailable;
          icon = "mdi:alert-circle-outline";
          accentColor = "#95a5a6";
        } else if (zoneStatus === "LOST") {
          label = t.zone.lost;
          icon = "mdi:signal-off";
          accentColor = "#f39c12";
        } else {
          switch (deviceClass) {
            case "door":
              label = stateOn ? t.zone.open : t.zone.closed;
              icon = stateOn ? "mdi:door-open" : "mdi:door-closed";
              break;
            case "window":
              label = stateOn ? t.zone.open : t.zone.closed;
              icon = stateOn ? "mdi:window-open" : "mdi:window-closed";
              break;
            case "smoke":
              label = stateOn ? t.zone.smoke : t.zone.clear;
              icon = stateOn ? "mdi:smoke-detector-alert" : "mdi:smoke-detector";
              break;
            default:
              label = stateOn ? t.zone.motion : t.zone.no_motion;
              icon = stateOn ? "mdi:motion-sensor" : "mdi:motion-sensor-off";
              break;
          }
        }
        if (isBypass) label += `, ${t.zone.bypass}`;

        return { sensor, deviceClass, isBypass, label, icon, accentColor };
      })
      .sort((a, b) => {
        const classOrder = ["motion", "door", "window", "smoke"];
        const typeDiff = classOrder.indexOf(b.deviceClass) - classOrder.indexOf(a.deviceClass);
        if (typeDiff !== 0) return typeDiff;
        return (a.sensor.attributes.friendly_name || "").localeCompare(b.sensor.attributes.friendly_name || "");
      });

    // Partition status mapping
    const partitionStatusMap = {
      disarmed: { label: t.partition.disarmed, icon: "mdi:lock-open", color: "#2ecc71" },
      armed: { label: t.partition.armed, icon: "mdi:home-lock", color: "#f39c12" },
      armed_immediate: { label: t.partition.armed_immediate, icon: "mdi:lock", color: "#e74c3c" },
      exit: { label: t.partition.exit, icon: "mdi:lock-clock", color: "#f1c40f" },
      prealarm: { label: t.partition.prealarm, icon: "mdi:alert-circle", color: "#e74c3c" },
      alarm: { label: t.partition.alarm, icon: "mdi:alert-circle", color: "#e74c3c" },
      unknown: { label: t.partition.unknown, icon: "mdi:help-circle", color: "var(--secondary-text-color)" },
    };

    // Enrich and sort Partitions
    const partitionItems = partitionSensors
      .map((sensor) => {
        const statusRaw = sensor.attributes?.partition_status || "unknown";
        const statusKey = statusRaw.toLowerCase().replace(/\s+/g, "_");
        const statusInfo = partitionStatusMap[statusKey] || partitionStatusMap.unknown;

        return {
          sensor,
          label: statusInfo.label,
          icon: statusInfo.icon,
          color: statusInfo.color,
        };
      })
      .sort((a, b) => {
        return (a.sensor.attributes.friendly_name || "").localeCompare(b.sensor.attributes.friendly_name || "");
      });

    // Enrich and sort Buttons
    const buttonItems = buttonEntities
      .map((sensor) => ({
        sensor,
        label: sensor.attributes?.friendly_name || sensor.entity_id,
      }))
      .sort((a, b) => {
        return a.label.localeCompare(b.label);
      });

    return html`
      <ha-card>
        <div class="card-header">
          <div class="title">
            <ha-icon icon="mdi:shield-home"></ha-icon>
            <span>${cardTitle}</span>
          </div>
          <div class="status ${isOnline ? "online" : "offline"}">
            <span class="status-dot"></span>
            <span>${statusText}</span>
          </div>
        </div>

        ${partitionItems.length
          ? html`
              <div class="section-title">${t.sections.partitions}</div>
              <div class="grid partition-grid" style="--partition-columns: ${this.config.partition_columns || 4}">
                ${partitionItems.map(
                  (item) => html`
                    <div class="partition-item" title="${item.sensor.entity_id}">
                      <div class="partition-icon" style="background-color: ${item.color}20;">
                        <ha-icon icon="${item.icon}" style="color: ${item.color}; font-size: 1em;"></ha-icon>
                      </div>
                      <div style="flex:1; min-width:0;">
                        <div
                          style="font-size:0.95em; font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;"
                        >
                          ${this._stripKsenia(item.sensor.attributes.friendly_name) || item.sensor.entity_id}
                        </div>
                        <div style="font-size:0.8em; color:var(--secondary-text-color);">${item.label}</div>
                      </div>
                    </div>
                  `
                )}
              </div>
            `
          : ""}

        ${buttonItems.length
          ? html`
              <div class="section-title">${t.sections.buttons}</div>
              <div
                class="grid button-grid"
                style="--button-columns: ${this.config.button_columns || this.config.partition_columns || 4}"
              >
                ${buttonItems.map(
                  (item) => html`
                    <div
                      class="button-item"
                      title="${item.sensor.entity_id}"
                      @click=${() => this._handleButtonPress(item.sensor.entity_id)}
                    >
                      <ha-icon
                        icon="mdi:gesture-tap-button"
                        style="color: var(--accent-color, #3498db); font-size: 1em;"
                      ></ha-icon>
                      <div style="flex:1; min-width:0;">
                        <div
                          style="font-size:0.95em; font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;"
                        >
                          ${this._stripKsenia(item.label)}
                        </div>
                      </div>
                    </div>
                  `
                )}
              </div>
            `
          : ""}

        ${zoneItems.length
          ? html`
              <div class="section-title">${t.sections.zones}</div>
              <div class="grid zone-grid" style="--zone-columns: ${this.config.zone_columns || 4}">
                ${zoneItems.map(
                  (item) => html`
                    <div
                      class="zone-item${item.isBypass ? " bypass" : ""}"
                      title="${item.sensor.entity_id}"
                      @click=${() => this._handleZoneClick(item.sensor, t)}
                    >
                      <ha-icon class="zone-icon" icon="${item.icon}" style="color: ${item.accentColor};"></ha-icon>
                      <div style="flex:1; min-width:0;">
                        <div
                          style="font-size:0.95em; font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;"
                        >
                          ${this._stripKsenia(item.sensor.attributes.friendly_name) || item.sensor.entity_id}
                        </div>
                        <div style="font-size:0.8em; color:var(--secondary-text-color);">${item.label}</div>
                      </div>
                    </div>
                  `
                )}
              </div>
            `
          : ""}
      </ha-card>
    `;
  }

  _handleButtonPress(entityId) {
    this._fireHaptic("light");
    this.hass.callService("button", "press", { entity_id: entityId });
  }

  _handleZoneClick(sensor, t) {
    const name = this._stripKsenia(sensor.attributes.friendly_name) || sensor.entity_id;
    if (this.config.confirm_bypass) {
      if (!window.confirm(`${t.zone.confirm_bypass} "${name}" ?`)) {
        return;
      }
    }
    this._fireHaptic("light");
    this.hass.callService("ksenia", "zone_bypass", { entity_id: sensor.entity_id });
  }

  _fireHaptic(type = "light") {
    const event = new Event("haptic", { bubbles: true, composed: true });
    event.detail = type;
    this.dispatchEvent(event);
  }

  setConfig(config) {
    this.config = config;
  }

  getCardSize() {
    return 3;
  }

  _stripKsenia(name) {
    if (!name || typeof name !== "string") return name;
    return name.replace(/Ksenia Lares/gi, "").replace(/\s{2,}/g, " ").trim();
  }

  static getConfigElement() {
    return document.createElement("ksenia-card-editor");
  }
}

/**
 * UI Editor for Ksenia Lares Card
 */
class KseniaLaresCardEditor extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      _config: { type: Object },
    };
  }

  setConfig(config) {
    this._config = config;
  }

  render() {
    if (!this.hass || !this._config) {
      return html``;
    }

    const schema = [
      { name: "title", selector: { text: {} } },
      {
        name: "entity",
        selector: {
          entity: {
            domain: "binary_sensor",
            device_class: "connectivity",
            integration: "ksenia",
          },
        },
      },
      { name: "partition_columns", selector: { number: { min: 1, max: 8, step: 1 } } },
      { name: "button_columns", selector: { number: { min: 1, max: 8, step: 1 } } },
      { name: "zone_columns", selector: { number: { min: 1, max: 8, step: 1 } } },
      { name: "confirm_bypass", selector: { boolean: {} } },
    ];

    return html`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${schema}
        .computeLabel=${(s) => this._computeLabel(s)}
        @value-changed=${this._onValueChanged}
      ></ha-form>
    `;
  }

  _computeLabel(schema) {
    const t = getTranslations(this.hass);
    return t.editor[schema.name] || schema.name;
  }

  _onValueChanged(ev) {
    if (!this._config || !this.hass) {
      return;
    }

    const event = new CustomEvent("config-changed", {
      detail: { config: ev.detail.value },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }
}

if (!customElements.get("ksenia-card")) {
  customElements.define("ksenia-card", KseniaLaresCard);
}
if (!customElements.get("ksenia-card-editor")) {
  customElements.define("ksenia-card-editor", KseniaLaresCardEditor);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "ksenia-card")) {
  window.customCards.push({
    type: "ksenia-card",
    name: "Ksenia Lares Card",
    description:
      "A compact security dashboard card displaying Partitions, Scenarios, and Zones for the Ksenia Lares integration.",
    preview: true,
    documentationURL: "https://github.com/amg0/ha_ksenia",

    getEntitySuggestion: (hass, entityId) => {
      const entityReg = hass.entities?.[entityId];

      if (!entityReg || entityReg.platform !== "ksenia") {
        return null;
      }

      return {
        config: { type: "custom:ksenia-card" },
      };
    },
  });
}
