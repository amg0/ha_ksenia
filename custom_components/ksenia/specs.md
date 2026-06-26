# KSENIA Vera Plugin - Configuration & API Reference

## User Configurable Variables

These variables are used to configure the plugin's connection to the Ksenia system.

| Variable | Service ID | Description | Default |
| :--- | :--- | :--- | :--- |
| **ip** | _Device Attribute_ | The IP address of the Ksenia controller on the local network. | _None_ |
| **port** | _Device Attribute_ | The port of the Ksenia controller on the local network. | _None_ |
| **Credentials** | `urn:upnp-org:serviceId:ksenia1` | Base64 encoded `username:password` for HTTP authentication. | _None_ |
| **PIN** | `urn:upnp-org:serviceId:ksenia1` | Encrypted system PIN code for executing scenarios. | _None_ |
| **RefreshPeriod** | `urn:upnp-org:serviceId:ksenia1` | Polling interval (in seconds) for zone/partition status. | `5` |

INSTRUCTIONS:

config flow : the ip and the user and password credential
option flow : the resfreshperiod and the PIN code which must be a SECRET type of variable
reconfigure flow: the user and password credential

---

## API Specification

The plugin communicates with the Ksenia system via HTTP GET requests using Basic Authentication. All endpoints return XML data.

### System & Health Endpoints

* **`/xml/info/generalInfo.xml`**: Retrieves general hardware and system information.
* **`/xml/faults/faults.xml`**: Retrieves system health metrics, including power supply voltage, battery voltage, and ethernet connection status.
* **`/xml/log/log60.xml`**: Downloads the last 60 security system event logs.

### Zone Management

* **`/xml/zones/zonesDescription16IP.xml`**: Fetches the names and descriptions of all configured alarm zones.
* **`/xml/zones/zonesStatus16IP.xml`**: Polls the current state of all zones (e.g., NORMAL, ALARM).

### Partition Management

* **`/xml/partitions/partitionsDescription16IP.xml`**: Retrieves the names of configured partitions.
* **`/xml/partitions/partitionsStatus16IP.xml`**: Polls the current arming state/status of all partitions.

### Scenario (Macro) Execution

* **`/xml/scenarios/scenariosDescription.xml`**: Retrieves the list and descriptions of available scenarios.
* **`/xml/scenarios/scenariosOptions.xml`**: Fetches scenario properties (whether they are enabled and if they require a PIN).
* **`/xml/cmd/cmdOk.xml`**: Executes a specific scenario.
  * _Parameters:_ `cmd=setMacro`, `macroId=<id>`, `redirectPage=/xml/cmd/cmdError.xml`
  * _Optional Parameter:_ `pin=<pin>` (if required by the scenario).
