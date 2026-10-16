// Port of Nxp_pkg/NFCEE_Management.py: every handler delegates to the forum 2.0
// implementation (Origin.X(raw, "nxp")); NXP tables come in through ctx.
import forum from '../forum20/nfceeManagement.js';

const handlers = { ...forum };
export default handlers;
