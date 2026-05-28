// Standard Expo Metro config — must extend `expo/metro-config` so that the
// expo CLI's Metro pipeline (asset hashing, transformer, resolver) runs.
// Without this, the bundle can load on the device but key runtime hooks can
// misbehave silently. (Flagged by `npx expo-doctor`.)
const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

module.exports = config;
