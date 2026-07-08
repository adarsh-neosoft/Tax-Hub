import { Form } from "@/components/ui/form.tsx";
import { Card } from "@/components/ui/card.tsx";
import { Badge } from "@/components/ui/badge.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Spinner } from "@/components/ui/spinner.tsx";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion.tsx";

import StageFormFields from "./tds-opinion/StageFormFields";
import { ALL_SECTION_FIELDS } from "./tds-opinion/fieldConfig";


export default function WorkflowAccordion({
    form,
    accordionSections,
    sectionFieldsMap,
    editableSections,
    currentStage,
    openAccordion,
    setOpenAccordion,
    queryClient,
    form146TypeData,
    poNpo,
    fileUrls,
    requestId,
    sectionFields,
    submitSection,
    saveMutation,
    handleClear,
    approvalMode,
}) {

    // Derive fields from data keys when sectionFieldsMap is not provided (e.g. approval mode)
    const deriveFields = (sectionKey) => {
        if (sectionFieldsMap) {
            return sectionFieldsMap[sectionKey] || [];
        }
        // Fallback: use field config from fieldConfig.js for labels and proper types
        const configFields = ALL_SECTION_FIELDS[sectionKey] || [];
        const data = sectionFields?.[sectionKey];
        if (!data) return configFields;

        return Object.keys(data)
        .filter((key) => !key.endsWith('_display'))
        .map((key) => {
            const config = configFields.find((f) => f.key === key);
            return {
                key,
                label: config?.label || key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
                type: config?.type ||
                    (typeof data[key] === "object" && data[key] !== null && !Array.isArray(data[key])
                        ? "file"
                        : "text"),
                disabled: config?.disabled ?? false,
                ...(config?.api ? { api: config.api } : {}),
                ...(config?.labelFields ? { labelFields: config.labelFields } : {}),
                ...(config?.options ? { options: config.options } : {}),
                ...(config?.action ? { action: config.action } : {}),
                ...(config?.dropdownParams ? { dropdownParams: config.dropdownParams } : {}),
            };
        });
    };

    return (
        <Card size="sm" className="p-5 mb-4">
                    <Accordion type="single" collapsible value={openAccordion} onValueChange={setOpenAccordion}>
                      {accordionSections.map((section) => {
                        const fields = deriveFields(section.key);
                        const editable = editableSections.includes(section.key);
                        const sectionFileUrls = sectionFields?.[section.key] || {};

                        // In approval mode or when form146TypeData/poNpo not available, skip special field filtering
                        const useFormFiltering = !approvalMode && sectionFieldsMap;

                        let filteredFields = fields;

                        if (useFormFiltering && section.key === "bank_detail") {
                            filteredFields = fields.filter((field) => {
                                const selectedType = (
                                    form146TypeData?.type_15cb || ""
                                ).toLowerCase();

                                const showExternalCA =
                                    selectedType.includes("146") &&
                                    selectedType.includes("part c");

                                if (field.key === "external_ca" && !showExternalCA) {
                                    return false;
                                }

                                return true;
                            });
                        } else if (useFormFiltering && section.key === "master" && !poNpo) {
                            filteredFields = fields.filter(
                                (field) => field.key !== "po_number"
                            );
                        }
        
                        return (
                          <AccordionItem key={section.key} value={section.key}>
                            <AccordionTrigger className="text-base font-medium hover:no-underline">
                              <div className="flex items-center gap-2">
                                <span>{section.title}</span>
                                {section.stage === currentStage && (
                                  <Badge variant="default" className="text-xs">Current</Badge>
                                )}
                                {!editable && <Badge variant="secondary" className="text-xs">Read only</Badge>}
                              </div>
                            </AccordionTrigger>
                            <AccordionContent className="pt-2 pb-4">
                              <Form {...form}>
                                <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
                                  <StageFormFields
                                    control={form.control}
                                    sectionKey={section.key}
                                    fields={filteredFields}
                                    disabled={!editable}
                                    fileUrls={sectionFileUrls}
                                    requestId={requestId}
                                    values={form.watch()}
                                    onComparisonComplete={() => {
                                        queryClient?.invalidateQueries({ queryKey: ["tds-workflow-form", requestId] });
                                    }}
                                  />
                                  {editable && saveMutation && handleClear && submitSection && (
                                    <div className="flex justify-end gap-2 pt-4 border-t">
                                      <Button
                                        type="button"
                                        variant="outline"
                                        onClick={handleClear}
                                        disabled={saveMutation.isPending}
                                      >
                                        Cancel
                                      </Button>
                                      <Button
                                        type="button"
                                        onClick={() => submitSection(section.key)}
                                        disabled={saveMutation.isPending}
                                      >
                                        {saveMutation.isPending && <Spinner className="mr-2" />}
                                        Save
                                      </Button>
                                    </div>
                                  )}
                                </form>
                              </Form>
                            </AccordionContent>
                          </AccordionItem>
                        );
                      })}
                    </Accordion>
                  </Card>
    );
}