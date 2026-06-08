import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export default {
  market: () => api.get("/market").then((r) => r.data),
  catalog: () => api.get("/catalog").then((r) => r.data),
  botQuote: (task_key, units_multiple) => api.post("/bot/quote", { task_key, units_multiple }).then((r) => r.data),
  botRequest: (message) => api.post("/bot/request", { message }).then((r) => r.data),
  submit: (requester, task_key, units_multiple) => api.post("/job/submit", { requester, task_key, units_multiple }).then((r) => r.data),
  complete: (id, quality) => api.post(`/job/${id}/complete`, { quality }).then((r) => r.data),
  jobs: (requester) => api.get("/job/list", { params: { requester } }).then((r) => r.data),
  registerProvider: (operator, gpus) => api.post("/provider/register", { operator, gpus }).then((r) => r.data),
  providers: (ranked = true) => api.get("/providers", { params: { ranked: ranked ? 1 : "" } }).then((r) => r.data),
  heartbeat: (id, online) => api.post(`/provider/${id}/heartbeat`, { online }).then((r) => r.data),
  openSession: (agent, budget_sol) => api.post("/agent/session", { agent, budget_sol }).then((r) => r.data),
  runSession: (id, task_key, units_multiple) => api.post(`/agent/${id}/run`, { task_key, units_multiple }).then((r) => r.data),
  session: (id) => api.get(`/agent/${id}`).then((r) => r.data),
};
