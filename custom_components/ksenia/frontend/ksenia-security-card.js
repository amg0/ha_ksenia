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
    title: "Card Title (Optional)"
  },
  fr: {
    title: "Titre de la carte (Optionnel)"
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
    `;
  }

  static getStubConfig() {
    return {
      title: "KSenia V3 Panel"
    };
  }

  shouldUpdate(changedProps) {
    if (changedProps.has('config')) return true;

    if (changedProps.has('hass')) {
      const oldHass = changedProps.get('hass');
      if (!oldHass) return true;

      for (const entityId in this.hass.states) {
        const stateObj = this.hass.states[entityId];
        if (stateObj.attributes && stateObj.attributes.device_class === 'connectivity') {
          if (oldHass.states[entityId] !== stateObj) {
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

    const connectionEntity = Object.keys(this.hass.states)
      .map(id => this.hass.states[id])
      .find(stateObj => stateObj.attributes && stateObj.attributes.device_class === 'connectivity');

    const isOnline = connectionEntity ? connectionEntity.state === 'on' : false;
    const statusText = connectionEntity ? (isOnline ? "Online" : "Offline") : "No sensor";

    const cardTitle = this.config.title || (connectionEntity?.attributes.friendly_name ? connectionEntity.attributes.friendly_name.replace(" API connectivity", "") : "KSenia V3 Panel");

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

        ${connectionEntity ? html`
          <div style="text-align: center; padding: 16px 0;">
            <ha-icon
              icon="${isOnline ? 'mdi:check-circle' : 'mdi:close-circle'}"
              style="font-size: 3em; color: ${isOnline ? '#2ecc71' : '#e74c3c'};"
            ></ha-icon>
            <div style="margin-top: 12px; font-size: 0.9em; color: var(--secondary-text-color);">
              ${connectionEntity.attributes.friendly_name || 'API Connectivity'}
            </div>
          </div>
        ` : html`
          <div style="padding: 20px 0; text-align: center; color: var(--secondary-text-color); font-style: italic;">
            No API connectivity sensor found.
          </div>
        `}
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
      {
        name: "title",
        selector: { text: {} }
      }
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
