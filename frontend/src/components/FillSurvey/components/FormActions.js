import React from 'react';

const FormActions = ({ submitting }) => (
  <div className="form-actions">
    <button type="submit" className="submit-btn" disabled={submitting}>
      {submitting ? 'Submitting...' : 'Submit Responses'}
    </button>
  </div>
);

export default FormActions; 