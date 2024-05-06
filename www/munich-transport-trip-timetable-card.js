// Munich Transport Trip Timetable Card

class MunichTransportTripTimetableCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({
            mode: 'open'
        });
    }

    /* This is called every time sensor is updated */
    set hass(hass) {

        const config = this.config;
        const maxEntries = config.max_entries || 10;
        const showTripName = config.show_trip_name || true;
        const entityIds = config.entity ? [config.entity] : config.entities || [];
        const stationMaxLen = config.station_name_max_length || 30;

        let content = "";

        for (const entityId of entityIds) {
            const entity = hass.states[entityId];
            if (!entity) {
                throw new Error("Entity State Unavailable");
            }

            if (showTripName) {
                content += `<div class="stop">${entity.attributes.friendly_name}</div>`;
            }
            content += `<div class="departure">
            <div class="header">Line</div>
            <div class="header">Departure</div>
            <div class="header">Destination</div>
            <div class="header">Arrival</div>
            </div>`
            const timetable = entity.attributes.departures.slice(0, maxEntries).map((departure) =>
                `<div class="departure">
                    <div class="line">
                        <div class="line-icon" style="background-color: ${departure.color}">${departure.line_name}</div>
                    </div>
                    <div class="time">${departure.human_departure_in_minutes}</div>
                    <div class="destination">${(departure.destination_station.length > stationMaxLen)
                    ? departure.destination_station.slice(0, stationMaxLen - 3) + '...'
                    : departure.destination_station}</div>
                    <div class="arrival">${departure.destination_real}</div>
                </div>`
            );

            content += `<div class="departures">` + timetable.join("\n") + `</div>`;
        }

        this.shadowRoot.getElementById('container').innerHTML = content;
    }

    /* This is called only when config is updated */
    setConfig(config) {
        const root = this.shadowRoot;
        if (root.lastChild) root.removeChild(root.lastChild);

        this.config = config;

        const card = document.createElement('ha-card');
        const content = document.createElement('div');
        const style = document.createElement('style')

        style.textContent = `
            .container {
                padding: 10px;
                font-size: 130%;
                line-height: 1.5em;
            }
            .stop {
                font-weight: 700;
                width: 100%;
                text-align: left;
                padding: 10px 10px 5px 5px;
            }      
            .departures {
                width: 100%;
                font-weight: 400;
                line-height: 1.5em;
                padding-bottom: 20px;
            }
            .departure {
                white-space: nowrap;
                padding-top: 10px;
                display: grid;
                grid-template-columns: 70px 90px auto 70px; /* Define the column widths */
                gap: 20px;
            }
            .line {
                min-width: 70px;
                align-self: right;
            }
            .line-icon {
                display: inline-block;
                border-radius: 20px;
                padding: 7px 10px 5px;
                font-size: 120%;
                font-weight: 700;
                line-height: 1em;
                color: #FFFFFF;
                text-align: center;
            }
            .destination {
                text-align: right;
                padding-right: 5px;
            }
            .arrival {
                text-align: right;
            }
            .time {
                text-align: right;
                font-weight: 700;
                line-height: 2em;
                padding-right: 10px;
            }
            .header {
                font-weight: 400;
                line-height: 2em;
                padding-right: 5px;
                padding-left: 2px;
                text-align: center;
                opacity: 0.9;
                border-bottom: 1px solid lightgrey;
            }
        `;

        content.id = "container";
        content.className = "container";
        card.header = config.title;
        card.appendChild(style);
        card.appendChild(content);

        root.appendChild(card);
    }

    // The height of the card.
    getCardSize() {
        return 5;
    }
}

customElements.define('munich-transport-trip-timetable-card', MunichTransportTripTimetableCard);
