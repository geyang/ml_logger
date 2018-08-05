export function getKeys(record) {
    return Object.keys(record).filter(k => (record.hasOwnProperty(k) && k !== "_step"));// && k !== "_timestamp"));
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

export function matchExp(exp) {
    const regex = new RegExp(exp, 'i');
    return function (k) {
        return k.match(regex);
    }
}

export function recordsToSeries(records, yKey = null, xKey = "_step", title = null) {
    let line = [];
    records.forEach(function (r, i) {
        if (typeof r[yKey] !== "undefined" && r[yKey] !== null) {
            try {
                line.push({x: r[xKey] || i, y: r[yKey]});
            } catch (e) {
                line = [{x: r[xKey] || i, y: r[yKey]}];
            }
        }
    });
    return {title: title || yKey, data: line}
}

export function recordsToSerieses(records, xKey = "_step") {
    const lines = {};
    records.forEach(function (r, i) {
        getKeys(r).forEach(function (k) {
            if (typeof r[xKey] !== 'undefined' && typeof r[k] !== "undefined" && r[k] !== null) {
                try {
                    lines[k].push({x: r[xKey] || i, y: r[k]})
                } catch (e) {
                    lines[k] = [{x: r[xKey] || i, y: r[k]}]
                }
            }
        });
    });
    return Object.entries(lines).map(([t, l]) => ({title: t, data: l}));
}

function flattenObject(ob) {
    let toReturn = {};
    let flatObject;
    for (let i in ob) {
        if (!ob.hasOwnProperty(i)) {
            continue;
        }
        //Exclude arrays from the final result
        //Check this http://stackoverflow.com/questions/4775722/check-if-object-is-array
        if (ob[i] && Array === ob[i].constructor) {
            continue;
        }
        if ((typeof ob[i]) === 'object') {
            flatObject = flattenObject(ob[i]);
            for (let x in flatObject) {
                if (!flatObject.hasOwnProperty(x)) {
                    continue;
                }
                //Exclude arrays from the final result
                if (flatObject[x] && Array === flatObject.constructor) {
                    continue;
                }
                toReturn[i + (!!isNaN(x) ? '.' + x : '')] = flatObject[x];
            }
        } else {
            toReturn[i] = ob[i];
        }
    }
    return toReturn;
}

function assignTrueful(a, b) {
    const n = {...a};
    for (let k in b) if (b[k] !== null && b[k] !== undefined) n[k] = b[k];
    return n;
}

export function flattenParams(records) {
    //done: if b.key == null, do NOT over-write existing value;
    let obj = records.reduce((a, b) => assignTrueful(a, b), {});
    return flattenObject(obj);
}
