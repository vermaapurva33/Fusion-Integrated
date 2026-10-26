const { user_ref } = require('./factories'); // Assuming user_ref is defined in factories.js

describe('LeaveApplication Tests', () => {
  beforeAll(async () => {
    await user_ref(1001);
    await user_ref(1002);
  });

  test('Create LeaveApplication for CL type', async () => {
    const leaveTypeCode = "CL";
    // Use leaveTypeCode directly instead of its ID
    // ...
  });

  test('Update LeaveApplication status', async () => {
    const leaveTypeCode = "CL";
    // Use leaveTypeCode directly instead of its ID
    // ...
  });
});
