import JSON5 from "json5";
import jwt from 'jsonwebtoken';

const DEFAULT_KEY = "ml-logger";
let counter = 0;

class Store {
  constructor(defaultValue = null, storageKey = DEFAULT_KEY, compress = false) {
    this.key = storageKey;
    // todo: compression is not implemented
    // this.compress = compress;
    let serial = window.localStorage.getItem(storageKey);
    this.value = !serial ? defaultValue : JSON5.parse(serial);
    this.changeHandles = {};
  }

  subscribe(callback) {
    const id = counter++;
    this.changeHandles[id] = callback;
    return () => delete this.changeHandles[id]
  }

  set(value) {
    this.value = {...this.value, ...value};
    let serial = JSON5.stringify(this.value);
    window.localStorage.setItem(this.key, serial);
    Object.values(this.changeHandles).forEach(fn => fn(this.value))
  }

  selectProfile(id) {
    if (this.value.profiles.length > id)
      this.set({profile: this.value.profiles[id]})
  }

  addProfile(value) {
    this.set({
      profiles: [...this.value.profiles, value],
      profile: value
    })
  }

  deleteProfile(id) {
    const {profiles = [], profile = {}} = this.value;
    const newProfiles = [...profiles.slice(0, id), ...profiles.slice(id + 1)];
    const lastProfile = newProfiles.length ? newProfiles[newProfiles.length - 1] : {};
    this.set({
      profiles: newProfiles,
      profile: (profiles[id] === profile) ? lastProfile : profile
    })
  }

  register({username, url, accessToken}) {
    this.set({servers: [...this.value.servers, {username, url, accessToken}]})

  }

  auth(webToken) {
    const {username, authToken, url} = jwt.decode(webToken);
  }
}

const store = new Store({
  profiles: [],
  profile: null
});
export default store;
