import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
import { ChatRequest, ChatResponse, SessionState } from '../models/interfaces';
import { environment } from '../../environments/environment';

/**
 * HTTP client service for communicating with the CareerCompass AI backend.
 */
@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private readonly baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * Send a chat message to the multi-agent system.
   */
  sendMessage(request: ChatRequest): Observable<ChatResponse> {
    return this.http
      .post<ChatResponse>(`${this.baseUrl}/chat`, request)
      .pipe(retry(1), catchError(this.handleError));
  }

  /**
   * Retrieve the current session state.
   */
  getSession(sessionId: string): Observable<SessionState> {
    return this.http
      .get<SessionState>(`${this.baseUrl}/session/${sessionId}`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Retrieve the generated roadmap for a session.
   */
  getRoadmap(sessionId: string): Observable<any> {
    return this.http
      .get(`${this.baseUrl}/roadmap/${sessionId}`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Health check.
   */
  healthCheck(): Observable<any> {
    return this.http.get(`${this.baseUrl}/health`);
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An unexpected error occurred.';

    if (error.status === 429) {
      errorMessage =
        'You have reached the daily request limit. Please try again tomorrow.';
    } else if (error.status === 0) {
      errorMessage =
        'Cannot connect to the server. Please check if the backend is running.';
    } else if (error.error?.detail) {
      errorMessage = error.error.detail;
    } else if (error.error?.message) {
      errorMessage = error.error.message;
    }

    console.error('API Error:', error);
    return throwError(() => new Error(errorMessage));
  }
}
