
const HOST = process.env.MOLGENIS_APPS_HOST || "https://diagnostics-acc.molgeniscloud.org";
const SCHEMA = process.env.MOLGENIS_APPS_SCHEMA || "umdm";

const opts = { changeOrigin: true, secure: false };

module.exports = {
  "/graphql": {
    target: `${HOST}/${SCHEMA}`,
    ...opts,
  },
//   "**/graphql": { target: `${HOST}`, ...opts },
  "/api": { target: `${HOST}`, ...opts },
  "/apps": { target: `${HOST}`, ...opts },
  "/theme.css": { target: `${HOST}/${SCHEMA}`, ...opts },
};