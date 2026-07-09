# Changelog

## [0.5.0](https://github.com/amg0/ha_ksenia/compare/v0.2.15...v0.5.0) (2026-07-09)


### Features

* add new API to query Ksenia alarm model ([7146fca](https://github.com/amg0/ha_ksenia/commit/7146fca4f3f9f48fd01f8b1015d3e68b03baf652))
* support Ksenia models 16IP 48IP 128IP ([06b6cbb](https://github.com/amg0/ha_ksenia/commit/06b6cbbdae013d4ab1b023aea0af52f91ec2696b))


### Bug Fixes

* cleanup Nullable type for _alarminfo ([952aa1b](https://github.com/amg0/ha_ksenia/commit/952aa1bc6b653eedd90e6ce299bea06f2c137027))


### Maintenance

* bump versions to 0.5.0 ([53ad187](https://github.com/amg0/ha_ksenia/commit/53ad1873c56c89e625c5d74473c739970a3960a8))

## [0.2.15](https://github.com/amg0/ha_ksenia/compare/v0.2.14...v0.2.15) (2026-07-09)


### Features

* add new API to query Ksenia alarm model ([7146fca](https://github.com/amg0/ha_ksenia/commit/7146fca4f3f9f48fd01f8b1015d3e68b03baf652))
* support Ksenia models 16IP 48IP 128IP ([06b6cbb](https://github.com/amg0/ha_ksenia/commit/06b6cbbdae013d4ab1b023aea0af52f91ec2696b))


### Bug Fixes

* cleanup Nullable type for _alarminfo ([952aa1b](https://github.com/amg0/ha_ksenia/commit/952aa1bc6b653eedd90e6ce299bea06f2c137027))

## [0.2.14](https://github.com/amg0/ha_ksenia/compare/v0.2.13...v0.2.14) (2026-07-09)


### Bug Fixes

* logging improvements ([6764798](https://github.com/amg0/ha_ksenia/commit/6764798b44d7ba4bd8f8e9bdd8c4bc7f9baabd39))

## [0.2.13](https://github.com/amg0/ha_ksenia/compare/v0.2.12...v0.2.13) (2026-07-08)


### Bug Fixes

* force immediate data refresh when a button is clicked ([fd86549](https://github.com/amg0/ha_ksenia/commit/fd86549974a06000973529c66de7fd971e38884c))

## [0.2.12](https://github.com/amg0/ha_ksenia/compare/v0.2.11...v0.2.12) (2026-07-08)


### Features

* cllickable zone button on lovelace card to control the BYPASS state ([ca2fcd4](https://github.com/amg0/ha_ksenia/commit/ca2fcd4ccffd9a26957ffd9da8a07df1b5b30466))


### Bug Fixes

* cleanup code ([e4294ca](https://github.com/amg0/ha_ksenia/commit/e4294cae1de405d5886b49863a8013bb811bf7ff))

## [0.2.11](https://github.com/amg0/ha_ksenia/compare/v0.2.10...v0.2.11) (2026-07-08)


### Features

* optimize lovelace layout on phone ([7cda850](https://github.com/amg0/ha_ksenia/commit/7cda8509be30a306a2accafc53a79d2548af4bb7))

## [0.2.10](https://github.com/amg0/ha_ksenia/compare/v0.2.9...v0.2.10) (2026-07-07)


### Features

* Implement zone bypass service action for Ksenia integration in Home Assistant. ([f004e20](https://github.com/amg0/ha_ksenia/commit/f004e20bea43156abbcc90dd818a0f922399e768))
* localization FR for scenario helper text ([67f9a1f](https://github.com/amg0/ha_ksenia/commit/67f9a1f756731ddc4ff460e8bdc9a9c07ebc5f8a))
* proper declaration of the service zone_bypass ([aa8ac62](https://github.com/amg0/ha_ksenia/commit/aa8ac6269a3b53149fe1261c7bf61a9e60fc4a9a))
* trigger instantaneous refresh after Scenario Run ([b8752f1](https://github.com/amg0/ha_ksenia/commit/b8752f134f3faa71bdfbe704267f06db8d628c16))


### Bug Fixes

* 1 based indexing in the KSenia Zone API ([aa8ac62](https://github.com/amg0/ha_ksenia/commit/aa8ac6269a3b53149fe1261c7bf61a9e60fc4a9a))

## [0.2.9](https://github.com/amg0/ha_ksenia/compare/v0.2.8...v0.2.9) (2026-07-07)


### Features

* add a special attribute "integration" to entities created by "ksenia" integration ([8cf9472](https://github.com/amg0/ha_ksenia/commit/8cf9472e45a2301ad2614898d88c539fa30b89db))
* add filter on lovelace card to only consider ksenia ([ccfa03d](https://github.com/amg0/ha_ksenia/commit/ccfa03d3643e52df81e89db02ec4a966abce7915))


### Bug Fixes

* attributes value should be pure string ([e1e585d](https://github.com/amg0/ha_ksenia/commit/e1e585d13520df60ea72bec418b1303627cdee73))

## [0.2.8](https://github.com/amg0/ha_ksenia/compare/v0.2.7...v0.2.8) (2026-07-07)


### Features

* show bypassed resources ([20d8458](https://github.com/amg0/ha_ksenia/commit/20d84588e0b5fec7f427ad0de8b5e51442656424))

## [0.2.7](https://github.com/amg0/ha_ksenia/compare/v0.2.6...v0.2.7) (2026-07-06)


### Features

* partitions icons in lovelace card, parameter to control nomber of displayed columns ([7ee3491](https://github.com/amg0/ha_ksenia/commit/7ee34918f70df553cb0c125fc1645a6ec818fd78))


### Bug Fixes

* improve client colors ([29dc966](https://github.com/amg0/ha_ksenia/commit/29dc966017cc53c89050d1657a7a84a488e4740f))
* namings ([87c60aa](https://github.com/amg0/ha_ksenia/commit/87c60aa164f3b910a818cbd03560b1f9809a8de6))
* progress on strongly type for the api client ([0873ec4](https://github.com/amg0/ha_ksenia/commit/0873ec42061218a8eef1524f344d94092f6c5978))
* strong typing for partition status and partition data and bug fixes for partition binary sensor ([b5e08d2](https://github.com/amg0/ha_ksenia/commit/b5e08d268b13f8c867bfcdd785b5f4d33e45f118))
* stronger typing in Run Scenario code ([b233b39](https://github.com/amg0/ha_ksenia/commit/b233b39a112884f2182e13871d847a2c4dd1c741))
* use of StrEnum instead of Enum ([7ee3491](https://github.com/amg0/ha_ksenia/commit/7ee34918f70df553cb0c125fc1645a6ec818fd78))

## [0.2.6](https://github.com/amg0/ha_ksenia/compare/v0.2.5...v0.2.6) (2026-07-03)


### Bug Fixes

* stronger typing for the client API ([aacff9f](https://github.com/amg0/ha_ksenia/commit/aacff9f3768bca2e1700798b2b1a2ca3a386c948))

## [0.2.5](https://github.com/amg0/ha_ksenia/compare/v0.2.4...v0.2.5) (2026-07-03)


### Features

* display zone an add a config option to set the number of columns for zones ([4b9c30c](https://github.com/amg0/ha_ksenia/commit/4b9c30c00460e6874cab73af6beddaffef63fb53))

## [0.2.4](https://github.com/amg0/ha_ksenia/compare/v0.2.3...v0.2.4) (2026-07-03)


### Features

* first working lovelace card version ([d2fb619](https://github.com/amg0/ha_ksenia/commit/d2fb619edd3c7ec1194db85c5ca2772e63f2aa41))

## [0.2.3](https://github.com/amg0/ha_ksenia/compare/v0.2.2...v0.2.3) (2026-07-03)


### Features

* ksenia lovelace card ( not working yet ) ([68e5194](https://github.com/amg0/ha_ksenia/commit/68e51941a1966d42aeec21d69a2cfb5fb1d76916))


### Bug Fixes

* minor test in progress ([82b1c57](https://github.com/amg0/ha_ksenia/commit/82b1c57ecd52bf08a6bb0fc0d2dc0f20b231fb72))

## [0.2.2](https://github.com/amg0/ha_ksenia/compare/v0.2.1...v0.2.2) (2026-07-01)


### Bug Fixes

* add PIN code to run scenario command and tested working. ([59ace93](https://github.com/amg0/ha_ksenia/commit/59ace937e4553586b98753a2aa113e54e2624782))

## [0.2.1](https://github.com/amg0/ha_ksenia/compare/v0.2.0...v0.2.1) (2026-07-01)


### Features

* Button platform to trigger the execution of a KSenia Scenario when the button is clicked ([edad721](https://github.com/amg0/ha_ksenia/commit/edad721ad09e933a2645b1d5c8bd2b96e530989b))

## [0.2.0](https://github.com/amg0/ha_ksenia/compare/v0.1.1...v0.2.0) (2026-06-29)


### Features

* add new API for scenario detection and a custom service to run a scenario ([3f56498](https://github.com/amg0/ha_ksenia/commit/3f56498dfcd2ca153a76fccf1e92a4b6ecbba0cf))
* version bump ([756738c](https://github.com/amg0/ha_ksenia/commit/756738c2feda5d5240e28f37fb1db8cf3852cd2f))

## [0.1.1](https://github.com/amg0/ha_ksenia/compare/v0.1.0...v0.1.1) (2026-06-26)


### Features

* add port configuration and usage in API client ([aacd993](https://github.com/amg0/ha_ksenia/commit/aacd99309fc8172d7499d5f9389747eca3db4cf6))
* implement two-step configuration flow ([5f9027f](https://github.com/amg0/ha_ksenia/commit/5f9027f491c149f78f8b50ec8d7ee4529cf514f5))


### Bug Fixes

* Add port parameter to KseniaLaresApiClient in credentials.py and config_flow.py ([8bee804](https://github.com/amg0/ha_ksenia/commit/8bee8043ad68c56e2ce89c040501825dd1de1d89))
* Remove default port and update URL construction ([e587cd2](https://github.com/amg0/ha_ksenia/commit/e587cd26949976df3a27498c942f7aaeeb4bb0ab))
