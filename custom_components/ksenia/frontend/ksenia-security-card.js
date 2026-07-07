/**
 * KSenia V3 Lovelace Card
 * A synthetic and dense dashboard card for GCE KSenia V3 integrations.
 */

// We can load LitElement from the Home Assistant frontend helper if available,
// otherwise fall back to a public CDN.
const LitElement = Object.getPrototypeOf(customElements.get("ha-panel-lovelace") || HTMLElement);
const { html, css } = LitElement.prototype;

const editorTranslations = {
  en: {
    title: "Card Title (Optional)",
    zone_columns: "Number of columns for zones (default 4)",
    partition_columns: "Number of columns for partitions (default 4)"
  },
  fr: {
    title: "Titre de la carte (Optionnel)",
    zone_columns: "Nombre de colonnes pour les zones (default 4)",
    partition_columns: "Nombre de colonnes pour les partitions (default 4)"
  }
};

class KSeniaV3Card extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object }
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
        margin: 18px 0 10px 0; /* Légèrement augmenté pour aérer */
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
        gap: 8px;
        margin-bottom: 12px;
      }
      /* Relay Styles */
      .relay-grid {
        grid-template-columns: repeat(var(--relay-columns, 4), 1fr);
      }
      .relay-btn {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        padding: 10px 6px;
        text-align: center;
        cursor: pointer;
        font-size: 0.85em;
        font-weight: 500;
        transition: all 0.2s ease-in-out;
        user-select: none;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .relay-btn:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.2);
      }
      .relay-btn.active {
        background: rgba(46, 204, 113, 0.15);
        border-color: #2ecc71;
        color: #2ecc71;
        box-shadow: 0 0 8px rgba(46, 204, 113, 0.15);
      }
      /* Input Styles */
      .input-grid {
        grid-template-columns: repeat(var(--input-columns, 4), 1fr);
      }
      .input-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.03);
        padding: 8px;
        border-radius: 6px;
        font-size: 0.85em;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }
      .led {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: rgba(255, 255, 255, 0.15);
        flex-shrink: 0;
        transition: all 0.3s ease;
      }
      .led.active {
        background-color: #f1c40f;
        box-shadow: 0 0 8px #f1c40f;
      }
      /* Analog Styles */
      .analog-grid {
        grid-template-columns: repeat(var(--analog-columns, 2), 1fr);
        gap: 10px;
      }
      .analog-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
      }
      .analog-icon {
        color: var(--paper-item-icon-color, #3498db);
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(52, 152, 219, 0.1);
        padding: 8px;
        border-radius: 50%;
      }
      .analog-info {
        display: flex;
        flex-direction: column;
      }
      .analog-label {
        font-size: 0.75em;
        color: var(--secondary-text-color, #bac2de);
      }
      .analog-value {
        font-size: 1.05em;
        font-weight: 600;
      }
      /* Counter Styles */
      .counter-container {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }
      .counter-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 8px 12px;
        border-radius: 6px;
      }
      .counter-name {
        font-size: 0.9em;
      }
      .counter-value {
        font-weight: 600;
        font-size: 0.95em;
        margin-left: 4px;
        color: var(--accent-color, #ff007f);
      }
      .counter-actions {
        display: flex;
        gap: 4px;
      }
      .counter-actions mwc-button {
        --mdc-theme-primary: var(--primary-text-color);
      }
      .counter-btn {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        color: var(--primary-text-color);
        cursor: pointer;
        padding: 4px 10px;
        font-size: 0.85em;
        font-weight: bold;
        transition: background 0.1s ease;
      }
      .counter-btn:hover {
        background: rgba(255, 255, 255, 0.15);
      }
      .counter-btn:active {
        background: rgba(255, 255, 255, 0.25);
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
        padding: 8px;
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
        padding: 8px;
        border-radius: 6px;
        font-size: 0.85em;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }
      .zone-item.bypass {
        border-color: rgba(241, 196, 15, 0.3);
        background: rgba(241, 196, 15, 0.05);
      }
      .zone-item.bypass .analog-icon {
        position: relative;
      }
      .zone-item.bypass .analog-icon::after {
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
        padding: 8px;
        border-radius: 6px;
        font-size: 0.85em;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
      }
      .button-item:hover {
        background: rgba(0, 0, 0, 0.12);
        border-color: rgba(255, 255, 255, 0.15);
      }
    `;
  }

  static getStubConfig() {
    return {
      title: "KSenia V3 Panel",
      zone_columns: 4,
      partition_columns: 4
    };
  }

  shouldUpdate(changedProps) {
    if (changedProps.has('config')) return true;

    if (changedProps.has('hass')) {
      const oldHass = changedProps.get('hass');
      if (!oldHass) return true;

      for (const entityId in this.hass.states) {
        const stateObj = this.hass.states[entityId];
        const oldStateObj = oldHass.states[entityId];

        // Process only if the state changed
        if (stateObj !== oldStateObj) {
          const attr = stateObj.attributes;

          // Optimization: Check if it's our Ksenia integration
          if (attr && attr.integration && attr.integration.toLowerCase() === 'ksenia') {
            const deviceClass = attr.device_class;

            const isConnectivity = deviceClass === 'connectivity';
            const isZoneBinary = entityId.startsWith('binary_sensor.') && (deviceClass === 'door' || deviceClass === 'motion');
            const isPartition = entityId.startsWith('binary_sensor.') && deviceClass === 'lock';
            const isButton = entityId.startsWith('button.');

            if (isConnectivity || isZoneBinary || isPartition || isButton) {
              return true; // Fast exit, trigger render
            }
          }
        }
      }
      return false;
    }
    return true;
  }

  render() {
    if (!this.hass || !this.config) return html``;

    let connectionEntity = null;
    const zoneSensors = [];
    const partitionSensors = [];
    const buttonEntities = [];

    // Optimization: Single-pass iteration to categorize all Ksenia entities
    for (const entityId in this.hass.states) {
      const stateObj = this.hass.states[entityId];
      const attr = stateObj.attributes;

      // Restrict entirely to integration: Ksenia
      if (!attr || !attr.integration || attr.integration.toLowerCase() !== 'ksenia') continue;

      if (attr.device_class === 'connectivity') {
        connectionEntity = stateObj;
      } else if (entityId.startsWith('binary_sensor.')) {
        if (attr.device_class === 'door' || attr.device_class === 'motion') {
          zoneSensors.push(stateObj);
        } else if (attr.device_class === 'lock') {
          partitionSensors.push(stateObj);
        }
      } else if (entityId.startsWith('button.')) {
        buttonEntities.push(stateObj);
      }
    }

    const isOnline = connectionEntity ? connectionEntity.state === 'on' : false;
    const statusText = connectionEntity ? (isOnline ? "Online" : "Offline") : "No sensor";

    const rawTitle = this.config.title || (connectionEntity?.attributes.friendly_name ? connectionEntity.attributes.friendly_name.replace(" API connectivity", "") : "KSenia V3 Panel");
    const cardTitle = this._stripKsenia(rawTitle);

    // Enrich and sort Zones
    const zoneItems = zoneSensors.map(sensor => {
      const attr = sensor.attributes;
      const isDoor = attr.device_class === 'door';
      const stateOn = sensor.state === 'on';
      const isBypass = String(attr.bypass || '').toUpperCase() === 'BYPASS';

      let label = isDoor ? (stateOn ? 'Open' : 'Closed') : (stateOn ? 'Motion' : 'No motion');
      if (isBypass) label += ', bypass';

      return { sensor, isDoor, isBypass, label };
    }).sort((a, b) => {
      const typeDiff = (b.isDoor - a.isDoor);
      if (typeDiff !== 0) return typeDiff;
      return (a.sensor.attributes.friendly_name || '').localeCompare(b.sensor.attributes.friendly_name || '');
    });

    // Partition status mapping
    const partitionStatusMap = {
      'disarmed': { label: 'Disarmed', icon: 'mdi:lock-open', color: '#2ecc71' },
      'armed': { label: 'Armed', icon: 'mdi:home-lock', color: '#f39c12' },
      'armed_immediate': { label: 'Armed Immediate', icon: 'mdi:lock', color: '#e74c3c' },
      'exit': { label: 'Exit', icon: 'mdi:lock-clock', color: '#f1c40f' },
      'prealarm': { label: 'Prealarm', icon: 'mdi:alert-circle', color: '#e74c3c' },
      'alarm': { label: 'Alarm', icon: 'mdi:alert-circle', color: '#e74c3c' },
      'unknown': { label: 'Unknown', icon: 'mdi:help-circle', color: 'var(--secondary-text-color)' },
    };

    // Enrich and sort Partitions
    const partitionItems = partitionSensors.map(sensor => {
      const statusRaw = sensor.attributes?.partition_status || 'unknown';
      const statusKey = statusRaw.toLowerCase().replace(/\s+/g, '_');
      const statusInfo = partitionStatusMap[statusKey] || partitionStatusMap['unknown'];

      return {
        sensor,
        label: statusInfo.label,
        icon: statusInfo.icon,
        color: statusInfo.color,
      };
    }).sort((a, b) => {
      return (a.sensor.attributes.friendly_name || '').localeCompare(b.sensor.attributes.friendly_name || '');
    });

    // Enrich and sort Buttons
    const buttonItems = buttonEntities.map(sensor => ({
      sensor,
      label: sensor.attributes?.friendly_name || sensor.entity_id,
    })).sort((a, b) => {
      return a.label.localeCompare(b.label);
    });

    return html`
      <ha-card>
        <div class="card-header">
          <div class="title">
            <ha-icon icon="mdi:ip-network"></ha-icon>
            <span>${cardTitle}</span>
          </div>
          <div class="status ${isOnline ? 'online' : 'offline'}">
            <span class="status-dot"></span>
            <span>${statusText}</span>
          </div>
        </div>

        ${partitionItems && partitionItems.length ? html`
          <div class="section-title">Partitions</div>
          <div class="grid partition-grid" style="--partition-columns: ${this.config.partition_columns || 4}">
            ${partitionItems.map(item => html`
              <div class="partition-item" title="${item.sensor.entity_id}">
                <div class="partition-icon" style="background-color: ${item.color}20;">
                  <ha-icon icon="${item.icon}" style="color: ${item.color}; font-size: 1em;"></ha-icon>
                </div>
                <div style="flex:1; min-width:0;">
                  <div style="font-size:0.95em; font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${this._stripKsenia(item.sensor.attributes.friendly_name) || item.sensor.entity_id}</div>
                  <div style="font-size:0.8em; color:var(--secondary-text-color);">${item.label}</div>
                </div>
              </div>
            `)}
          </div>
        ` : ''}

        ${buttonItems && buttonItems.length ? html`
          <div class="section-title">Buttons</div>
          <div class="grid button-grid" style="--button-columns: ${this.config.partition_columns || 4}">
            ${buttonItems.map(item => html`
              <div class="button-item" title="${item.sensor.entity_id}" @click=${() => this.hass.callService('button', 'press', { entity_id: item.sensor.entity_id })}>
                <ha-icon icon="mdi:gesture-tap-button" style="color: var(--accent-color, #3498db); font-size: 1em;"></ha-icon>
                <div style="flex:1; min-width:0;">
                  <div style="font-size:0.95em; font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${this._stripKsenia(item.label)}</div>
                </div>
              </div>
            `)}
          </div>
        ` : ''}

        ${zoneItems && zoneItems.length ? html`
          <div class="section-title">Zones</div>
          <div class="grid zone-grid" style="--zone-columns: ${this.config.zone_columns || 4}">
            ${zoneItems.map(item => html`
              <div class="zone-item${item.isBypass ? ' bypass' : ''}" title="${item.sensor.entity_id}">
                <ha-icon
                  class="analog-icon"
                  icon="${item.isDoor ? 'mdi:door' : 'mdi:motion-sensor'}"
                  style="color: ${item.sensor.state === 'on' ? (item.isDoor ? '#e6311d' : '#ef9b0a') : 'var(--secondary-text-color)'};"
                ></ha-icon>
                <div style="flex:1; min-width:0;">
                  <div style="font-size:0.95em; font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${this._stripKsenia(item.sensor.attributes.friendly_name) || item.sensor.entity_id}</div>
                  <div style="font-size:0.8em; color:var(--secondary-text-color);">${item.label}</div>
                </div>
              </div>
            `)}
          </div>
        ` : ''}
      </ha-card>
    `;
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
    if (!name || typeof name !== 'string') return name;
    return name.replace(/Ksenia Lares/gi, '').replace(/\s{2,}/g, ' ').trim();
  }

  static getConfigElement() {
    return document.createElement("ksenia-card-editor");
  }
}

/**
 * UI Editor for KSenia V3 Card
 */
class KSeniaV3CardEditor extends LitElement {
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
      { name: "zone_columns", selector: { number: { min: 1, max: 8, step: 1 } } },
      { name: "partition_columns", selector: { number: { min: 1, max: 8, step: 1 } } }
    ];

    return html`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${schema}
        .computeLabel=${(schema) => this._computeLabel(schema)}
        @value-changed=${this._onValueChanged}
      ></ha-form>
    `;
  }

  _computeLabel(schema) {
    const lang = this.hass?.language || 'en';
    const baseLang = lang.split('-')[0];
    const dict = editorTranslations[baseLang] || editorTranslations['en'];
    return dict[schema.name] || schema.name;
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

customElements.define('ksenia-card', KSeniaV3Card);
customElements.define("ksenia-card-editor", KSeniaV3CardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'ksenia-card',
  name: 'KSenia V3 Card',
  description: 'A dense synthetic card displaying Relays, Digital Inputs, Analogs, and Counters for KSenia V3 custom integration.',
  preview: true,
  documentationURL: 'https://github.com/amg0/ha_KSeniav3',

  getEntitySuggestion: (hass, entityId) => {
    const entityReg = hass.entities[entityId];

    if (!entityReg || entityReg.platform !== "ksenia") {
      return null;
    }

    return {
      config: { type: "custom:ksenia-card" },
    };
  },
});
