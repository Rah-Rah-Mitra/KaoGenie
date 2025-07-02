
import { API_BASE_URL } from '../constants';
import { ExamFromTopicRequest, FullExam, ExamQuestion } from '../types';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `API Error: ${response.status} ${response.statusText}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch (e) {
      // Ignore if response is not JSON
    }
    throw new Error(errorMessage);
  }
  return response.json() as Promise<T>;
}


export interface StreamCallbacks {
  onProgress: (progress: { step: string; status: string }) => void;
  onLog: (log: { message: string }) => void;
  onResult: (result: FullExam) => void;
  onError: (error: { detail: string }) => void;
  onEnd: () => void;
}

async function processStream(response: Response, callbacks: StreamCallbacks) {
  if (!response.body) {
    throw new Error("Response body is null");
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  const processBuffer = () => {
    // Split buffer by the SSE message delimiter
    const parts = buffer.split('\n\n');
    // The last part might be incomplete, so keep it in the buffer
    buffer = parts.pop() || '';

    for (const part of parts) {
      if (!part) continue;

      let event = 'message';
      let dataString = '';
      
      for (const line of part.split('\n')) {
        if (line.startsWith('event: ')) {
          event = line.substring(7).trim();
        } else if (line.startsWith('data: ')) {
          dataString += line.substring(6);
        }
      }

      if (dataString) {
        try {
          const parsedData = JSON.parse(dataString.trim());
          switch (event) {
            case 'progress':
              callbacks.onProgress(parsedData);
              break;
            case 'log':
              callbacks.onLog(parsedData);
              break;
            case 'final_result':
              callbacks.onResult(parsedData as FullExam);
              break;
            case 'error':
              callbacks.onError(parsedData);
              break;
            case 'end_stream':
              callbacks.onEnd();
              return true; // Signal to stop processing
          }
        } catch (e) {
          console.error('Failed to parse SSE data chunk:', dataString, e);
        }
      }
    }
    return false; // Continue processing
  };

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      processBuffer(); // process any remaining data
      callbacks.onEnd();
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    if (processBuffer()) {
      await reader.cancel();
      break;
    }
  }
}

export const generateExamFromTopic = async (data: ExamFromTopicRequest, callbacks: StreamCallbacks): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/exam/from-topic`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    // This will throw on non-2xx responses before streaming begins
    await handleResponse<any>(response); 
  }
  await processStream(response, callbacks);
};

export const generateExamFromFile = async (formData: FormData, callbacks: StreamCallbacks): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/exam/from-file`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    await handleResponse<any>(response);
  }
  await processStream(response, callbacks);
};

export const regenerateSingleQuestion = async (examId: string, questionId: string): Promise<ExamQuestion> => {
  const response = await fetch(`${API_BASE_URL}/exam/regenerate-question/${examId}/${questionId}`, {
    method: 'POST',
  });
  return handleResponse<ExamQuestion>(response);
};
