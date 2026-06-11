import { ALL_SECTION_FIELDS } from "./fieldConfig";

export function fieldName(sectionKey, key) {
  return `${sectionKey}.${key}`;
}

function readFieldValue(sectionValues, field) {
  const val = sectionValues?.[field.key];
  if (field.type === "checkbox") {
    return Boolean(val);
  }
  if (field.type === "fk") {
    return val != null && val !== "" ? Number(val) : null;
  }
  if (field.type === "file") {
    return undefined;
  }
  if (val === "" || val === null || val === undefined) {
    return null;
  }
  return val;
}

function writeFieldDefault(field) {
  if (field.type === "checkbox") {
    return false;
  }
  if (field.type === "file") {
    return null;
  }
  return "";
}

function writeFieldFormValue(field, val) {
  if (field.type === "checkbox") {
    return Boolean(val);
  }
  if (field.type === "fk") {
    return val != null && val !== "" ? String(val) : "";
  }
  if (field.type === "file") {
    return null;
  }
  if (val === null || val === undefined) {
    return "";
  }
  return String(val);
}

/** Default values for a single section — nested shape for react-hook-form dot paths. */
export function sectionFormDefaults(fields, sectionKey) {
  const section = {};
  for (const field of fields) {
    section[field.key] = writeFieldDefault(field);
  }
  return { [sectionKey]: section };
}

/** Build API payload for one section from react-hook-form values. */
export function buildSectionPayload(values, sectionKey, fields) {
  const sectionValues = values?.[sectionKey] || {};
  const section = {};
  for (const field of fields) {
    const val = readFieldValue(sectionValues, field);
    if (val !== undefined) {
      section[field.key] = val;
    }
  }
  return section;
}

/** Convert API nested data to react-hook-form values (nested shape). */
export function nestedToFormValues(nestedData) {
  const values = {};
  for (const [sectionKey, fields] of Object.entries(ALL_SECTION_FIELDS)) {
    const sectionData = nestedData?.[sectionKey] || {};
    values[sectionKey] = {};
    for (const field of fields) {
      values[sectionKey][field.key] = writeFieldFormValue(field, sectionData[field.key]);
    }
  }
  return values;
}

export function formValuesToNested(values) {
  const nested = {};
  for (const [sectionKey, fields] of Object.entries(ALL_SECTION_FIELDS)) {
    nested[sectionKey] = buildSectionPayload(values, sectionKey, fields);
  }
  return nested;
}

export function collectFiles(values) {
  const files = {};
  for (const [sectionKey, fields] of Object.entries(ALL_SECTION_FIELDS)) {
    const sectionValues = values?.[sectionKey] || {};
    for (const field of fields) {
      if (field.type !== "file") continue;
      const file = sectionValues[field.key];
      if (file instanceof File) {
        files[`${sectionKey}.${field.key}`] = file;
      }
    }
  }
  return files;
}
