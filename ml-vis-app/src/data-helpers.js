export function getKeys(record) {
    return Object.keys(record).filter(k => (record.hasOwnProperty(k) && k !== "_step" && k !== "_timestamp"));
}

/** This only gets key from the first element in the record.
 * If the first record is no good, or if records have different keys,
 * use the index to point to the record you want.*/
export function getKeysFromRecords(records, index = 0) {
    if (records && records.length) {
        return getKeys(records[index])
    } else {
        return [];
    }
}

/** Maps a dictionary to an array. */
export function objectMapArray(o, fn) {
    return Object.keys(o).filter(k => o.hasOwnProperty(k)).map(k => o[k])
}

export function recordsToSeries(records) {
    const lines = {};
    for (let r of records) {
        getKeys(r).forEach(function (k) {
            try {
                lines[k].push({x: r._step, y: r[k]})
            } catch (e) {
                lines[k] = [{x: r._step, y: r[k]}]
            }
        });
    }
    return Object.entries(lines).map(([t, l]) => ({title: t, data: l}));
}

