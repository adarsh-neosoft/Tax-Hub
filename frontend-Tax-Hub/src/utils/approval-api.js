import { api } from "iron-stack-ui";

/**
 * Get approval page data using approval token.
 */
export async function getApproval(token) {
  return api.get(`/tax_requests/approval/${token}/`);
}

/**
 * Submit External CA action.
 *
 * action:
 *  - approve
 *  - reject
 *  - return
 */
export async function submitApproval({
  token,
  action,
  remarks = "",
  return_stage = null,
  form_146 = null,
}) {
  const payload = {
    action,
    remarks,
  };

  if (return_stage) {
    payload.return_stage = return_stage;
  }

  if (form_146 && Object.keys(form_146).length > 0) {
    payload.form_146 = form_146;
  }

  return api.post(
    `/tax_requests/approval/${token}/`,
    payload
  );
}