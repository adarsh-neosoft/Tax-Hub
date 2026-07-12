import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "iron-stack-ui";

import { Button } from "@/components/ui/button.tsx";
import { Input } from "@/components/ui/input.tsx";
import { Label } from "@/components/ui/label.tsx";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog.tsx";
import { Spinner } from "@/components/ui/spinner.tsx";

/**
 * Cancel button shown only at the TDS Opinion stage.
 * Prompts for remarks and confirmation before cancelling.
 * Once cancelled, navigates back to the list.
 */
export default function CancelButton({ requestId }) {
  const [showConfirm, setShowConfirm] = useState(false);
  const [remarks, setRemarks] = useState("");

  const cancelMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post(
        `/tax_requests/tdsopinion/${requestId}/cancel/`,
        { remarks }
      );
      return response.data;
    },
    onSuccess: (data) => {
      setShowConfirm(false);
      setRemarks("");
      toast.success("Request cancelled successfully.");
      // Navigate back to the list (same as old project's history.go(-1))
      window.history.back();
    },
    onError: (error) => {
      setShowConfirm(false);
      const message =
        error?.response?.data?.message ||
        error?.response?.data?.detail ||
        "Failed to cancel request.";
      toast.error(message);
    },
  });

  const handleCancel = () => {
    if (!remarks.trim()) {
      toast.error("Please enter remarks for cancellation.");
      return;
    }
    cancelMutation.mutate();
  };

  return (
    <>
      <Button
        type="button"
        variant="destructive"
        size="sm"
        onClick={() => setShowConfirm(true)}
        className="text-sm font-medium"
      >
        Cancel Request
      </Button>

      <Dialog open={showConfirm} onOpenChange={setShowConfirm}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Request</DialogTitle>
            <DialogDescription>
              Are you sure you want to cancel this request? This action cannot
              be undone. The request will be moved to the "Cancelled Requests"
              tab.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-2 py-2">
            <Label htmlFor="cancel-remarks">Remarks *</Label>
            <Input
              id="cancel-remarks"
              placeholder="Enter reason for cancellation"
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setShowConfirm(false);
                setRemarks("");
              }}
              disabled={cancelMutation.isPending}
            >
              No
            </Button>
            <Button
              type="button"
              variant="destructive"
              onClick={handleCancel}
              disabled={cancelMutation.isPending}
            >
              {cancelMutation.isPending && <Spinner className="mr-2 h-4 w-4" />}
              Yes, Cancel
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
