import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useForm } from "react-hook-form";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { MASTER_FIELDS, STAGE_FIELD_CONFIG } from "./tds-opinion/fieldConfig";
import ApprovalHierarchy from "./ApprovalHierarchy";
import WorkflowAccordion from "./WorkflowAccordion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Spinner } from "@/components/ui/spinner";
import { Form } from "@/components/ui/form";

import {
    getApproval,
    submitApproval,
} from "../utils/approval-api";

export default function ApprovalPage() {

    const navigate = useNavigate();

    const { token } = useParams();

    const [remarks, setRemarks] = useState("");

    const [returnStage, setReturnStage] = useState("");

    const [openAccordion, setOpenAccordion] = useState("");

    const [completed, setCompleted] = useState(false);

    const queryClient = useQueryClient();

    const form = useForm({
        defaultValues: {},
    });

    /**
     * ----------------------------------------------------------
     * Load approval payload
     * ----------------------------------------------------------
     */

    const approvalQuery = useQuery({

        queryKey: ["approval", token],

        queryFn: async () => {

            const response = await getApproval(token);

            return response.data;
        },

        retry: false,

    });

    /**
     * ----------------------------------------------------------
     * Submit action
     * ----------------------------------------------------------
     */

    const actionMutation = useMutation({

        mutationFn: async (payload) => {

            // Collect Form 146 stage fields from the form state
            // so they persist back to the normal workflow form
            const form146Values = form.getValues("form_146") || {};
            const form146Payload = {};

            // Only send fields that the External CA can edit
            const editableFields = ["remarks", "ack_number", "ack_date", "udin"];
            for (const key of editableFields) {
                const val = form146Values[key];
                if (val !== undefined && val !== null && val !== "") {
                    form146Payload[key] = val;
                }
            }

            const response = await submitApproval({
                token,
                form_146: form146Payload,
                ...payload,
            });

            return response.data;
        },

        onSuccess: (data) => {

            toast.success(data.message);

            setCompleted(true);

        },

        onError: (error) => {

            toast.error(

                error?.response?.data?.message ||

                error.message ||

                "Something went wrong."

            );

        },

    });

    /**
     * ----------------------------------------------------------
     * Prepare page data
     * ----------------------------------------------------------
     */

    const payload = approvalQuery.data?.payload;

    const stages = payload?.stages || [];

    const accordionSections = payload?.accordion_sections || [];

    const editableSections = ["form_146"];

    const currentStage = payload?.current_stage;

    const workflow = payload?.workflow;

    const nestedData = payload?.data || {};

    const sectionFieldsMap = useMemo(
        () => ({
            master: MASTER_FIELDS,
            ...STAGE_FIELD_CONFIG,
        }),
        [],
    );

    /**
     * ----------------------------------------------------------
     * Populate form
     * ----------------------------------------------------------
     */

    useEffect(() => {

        if (!nestedData) return;

        Object.entries(nestedData).forEach(

            ([sectionKey, values]) => {

                if (!values) return;

                Object.entries(values).forEach(

                    ([field, value]) => {

                        form.setValue(

                            `${sectionKey}.${field}`,

                            value

                        );

                    }

                );

            }

        );

    }, [nestedData]);

    /**
     * ----------------------------------------------------------
     * Auto open current section
     * ----------------------------------------------------------
     */

    useEffect(() => {

        if (!accordionSections.length) return;

        if (!currentStage) {

            setOpenAccordion(

                accordionSections[0].key

            );

            return;

        }

        const current = accordionSections.find(

            (item) => item.stage === currentStage

        );

        if (current) {

            setOpenAccordion(current.key);

        }

    }, [

        accordionSections,

        currentStage,

    ]);

    /**
     * ----------------------------------------------------------
     * Return stage dropdown
     * ----------------------------------------------------------
     */

    // Only allow revert/return to: Initiated, TDS Opinion, Invoice Posting, Bank Detail
    const ALLOWED_RETURN_STAGES = [
        "Initiated",
        "TDS Opinion",
        "Invoice Posting",
        "Bank Detail",
    ];

    const returnStageOptions = useMemo(() => {
        return stages.filter(
            (stage) =>
                ALLOWED_RETURN_STAGES.includes(stage) &&
                stage !== currentStage
        );
    }, [
        stages,
        currentStage,
    ]);

        /**
     * ----------------------------------------------------------
     * Loading
     * ----------------------------------------------------------
     */

    if (approvalQuery.isLoading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <Spinner size="lg" />
            </div>
        );
    }

    /**
     * ----------------------------------------------------------
     * Invalid / Expired Link
     * ----------------------------------------------------------
     */

    if (approvalQuery.isError) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-muted/30">
                <Card className="max-w-xl w-full p-8 text-center">

                    <h2 className="text-2xl font-bold text-red-600 mb-4">
                        Invalid Approval Link
                    </h2>

                    <p className="text-muted-foreground mb-6">
                        This approval link is invalid or has expired.
                    </p>

                    <Button
                        onClick={() => navigate("/")}
                    >
                        Close
                    </Button>

                </Card>
            </div>
        );
    }

    /**
     * ----------------------------------------------------------
     * Success Page
     * ----------------------------------------------------------
     */

    if (completed) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-muted/30">

                <Card className="max-w-xl w-full p-8 text-center">

                    <div className="text-6xl mb-6">
                        ✅
                    </div>

                    <h2 className="text-3xl font-bold mb-3">
                        Thank You
                    </h2>

                    <p className="text-muted-foreground mb-8">
                        Your response has been recorded successfully.
                    </p>

                    <p className="text-muted-foreground">
                        This approval link is no longer valid.
                    </p>

                </Card>

            </div>
        );
    }

    /**
     * ----------------------------------------------------------
     * Main UI
     * ----------------------------------------------------------
     */

    return (

        <div className="min-h-screen bg-muted/20 py-10">
            <div className="container max-w-7xl mx-auto">

                <Card className="p-6 mb-6">

                    <div className="flex justify-between items-center">

                        <div>

                            <h2 className="text-3xl font-bold">
                                External CA Approval
                            </h2>

                            <div className="text-muted-foreground mt-2">

                                Request :

                                <strong className="ml-2">

                                    {approvalQuery.data.request_code}

                                </strong>

                            </div>

                        </div>

                        <div>

                            <div className="text-sm text-muted-foreground">

                                Current Stage

                            </div>

                            <div className="font-semibold">

                                {currentStage}

                            </div>

                        </div>

                    </div>

                </Card>

                <ApprovalHierarchy
                    stages={stages}
                    currentStage={currentStage}
                />

                <Form {...form}>

                    <WorkflowAccordion

                        form={form}

                        accordionSections={accordionSections}

                        sectionFieldsMap={sectionFieldsMap}

                        editableSections={editableSections}

                        currentStage={currentStage}

                        openAccordion={openAccordion}

                        setOpenAccordion={setOpenAccordion}

                        sectionFields={nestedData}

                        requestId={approvalQuery.data.request_id}

                        approvalMode={true}

                        queryClient={queryClient}

                    />

                </Form>

                                <Card className="p-6 mt-6">

                    <h3 className="text-xl font-semibold mb-6">
                        External CA Action
                    </h3>

                    <div className="space-y-6">

                        {/* Remarks */}

                        <div>

                            <label className="block mb-2 font-medium">
                                Remarks
                            </label>

                            <Textarea
                                value={remarks}
                                onChange={(e) =>
                                    setRemarks(e.target.value)
                                }
                                rows={5}
                                placeholder="Enter remarks..."
                            />

                        </div>

                        {/* Return Stage */}

                        <div>

                            <label className="block mb-2 font-medium">
                                Return Stage
                            </label>

                            <select
                                className="w-full border rounded-md px-3 py-2"
                                value={returnStage}
                                onChange={(e) =>
                                    setReturnStage(e.target.value)
                                }
                            >

                                <option value="">
                                    Select Return Stage
                                </option>

                                {returnStageOptions.map((stage) => (

                                    <option
                                        key={stage}
                                        value={stage}
                                    >
                                        {stage}
                                    </option>

                                ))}

                            </select>

                        </div>

                        {/* Buttons */}

                        <div className="flex gap-4 pt-4">

                            <Button
                                disabled={actionMutation.isPending}
                                onClick={() =>
                                    actionMutation.mutate({
                                        action: "approve",
                                        remarks,
                                    })
                                }
                            >
                                Approve
                            </Button>

                            <Button
                                variant="destructive"
                                disabled={actionMutation.isPending}
                                onClick={() =>
                                    actionMutation.mutate({
                                        action: "reject",
                                        remarks,
                                    })
                                }
                            >
                                Reject
                            </Button>

                            <Button
                                variant="secondary"
                                disabled={
                                    actionMutation.isPending ||
                                    !returnStage
                                }
                                onClick={() =>
                                    actionMutation.mutate({
                                        action: "return",
                                        remarks,
                                        return_stage: returnStage,
                                    })
                                }
                            >
                                Return
                            </Button>

                        </div>

                    </div>

                </Card>

            </div>

        </div>

    );

}