export interface LeaveType {
  code: string;
}

export interface LeaveBalance {
  employee_id: number;
  balance: number;
}

export interface LeaveApplication {
  id: number;
  applicant_id: number;
  status: string;
  created_at: string;
}
