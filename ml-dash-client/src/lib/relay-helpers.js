import {Buffer} from 'buffer';

export function base64(i) {
  return new Buffer(i, 'utf8').toString('base64');
}

export function unbase64(i) {
  return new Buffer(i, 'base64').toString('utf8');
}

export function toGlobalId(type, id) {
  return base64([type, id].join(':'));
}

/**
 * Takes the "global ID" created by toGlobalID, and returns the type name and ID
 * used to create it.
 */
export function fromGlobalId(globalId) {
  const unbasedGlobalId = unbase64(globalId);
  const delimiterPos = unbasedGlobalId.indexOf(':');
  return {
    type: unbasedGlobalId.substring(0, delimiterPos),
    id: unbasedGlobalId.substring(delimiterPos + 1),
  };
}
