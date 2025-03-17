import React from 'react';

const FeedbackDialog = ({ 
  questionIndex, 
  feedbackInput,
  setFeedbackInput,
  onCancel,
  onSubmit
}) => {
  return (
    <div className="feedback-dialog-overlay">
      <div className="feedback-dialog">
        <h3>Regeneration of Question {questionIndex + 1}</h3>
        <p>Describe how you want to improve this question:</p>
        <textarea
          value={feedbackInput}
          onChange={(e) => setFeedbackInput(e.target.value)}
          placeholder="e.g. The question should be more detailed / simpler / include more options..."
          rows={4}
        />
        <div className="feedback-buttons">
          <button 
            onClick={onCancel}
            className="cancel-button"
          >
            Cancel
          </button>
          <button 
            onClick={onSubmit}
            className="submit-button"
          >
            Regenerate
          </button>
        </div>
      </div>
    </div>
  );
};

export default FeedbackDialog; 