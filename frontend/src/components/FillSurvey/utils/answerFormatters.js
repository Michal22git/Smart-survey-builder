export const formatAnswersForSubmission = (answers, questions) => {
  return Object.entries(answers).map(([questionId, answer]) => {
    const question = questions.find(q => q.id === parseInt(questionId));
    const questionType = question ? question.type : null;
    
    let formattedAnswer = {
      question: parseInt(questionId)
    };
    
    const safeParseInt = (value) => {
      if (value === null || value === undefined || value === '') {
        return null;
      }
      const parsed = parseInt(value);
      return isNaN(parsed) ? null : parsed;
    };
    
    if (questionType === 'text') {
      formattedAnswer.text_answer = answer || '';
      formattedAnswer.selected_options = [];
    } 
    else if (questionType === 'radio') {
      formattedAnswer.text_answer = null;
      const parsedOption = safeParseInt(answer);
      formattedAnswer.selected_options = parsedOption !== null ? [parsedOption] : [];
    }
    else if (questionType === 'checkbox') {
      formattedAnswer.text_answer = null;
      formattedAnswer.selected_options = Array.isArray(answer) && answer.length > 0 
        ? answer
            .map(opt => safeParseInt(opt))
            .filter(opt => opt !== null)
        : [];
    }
    else if (questionType === 'dropdown') {
      formattedAnswer.text_answer = null;
      const parsedOption = safeParseInt(answer);
      formattedAnswer.selected_options = parsedOption !== null ? [parsedOption] : [];
    }
    else {
      formattedAnswer.text_answer = typeof answer === 'string' ? answer : null;
      if (Array.isArray(answer) && answer.length > 0) {
        formattedAnswer.selected_options = answer
          .map(opt => safeParseInt(opt))
          .filter(opt => opt !== null);
      } else if (answer !== null && answer !== undefined) {
        const parsedOption = safeParseInt(answer);
        formattedAnswer.selected_options = parsedOption !== null ? [parsedOption] : [];
      } else {
        formattedAnswer.selected_options = [];
      }
    }
    
    return formattedAnswer;
  });
};