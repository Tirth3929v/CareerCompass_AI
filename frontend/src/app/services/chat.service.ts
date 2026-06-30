import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, finalize } from 'rxjs';
import { ApiService } from './api.service';
import {
  ChatMessage,
  ChatRequest,
  ChatResponse,
  ChallengeData,
  SkillScore,
  AnalysisResult,
  Roadmap,
} from '../models/interfaces';

/**
 * Manages chat state, message history, and session lifecycle.
 * Uses RxJS BehaviorSubjects for reactive state management.
 */
@Injectable({
  providedIn: 'root',
})
export class ChatService {
  /** Stream of all chat messages. */
  private messagesSubject = new BehaviorSubject<ChatMessage[]>([]);
  messages$: Observable<ChatMessage[]> = this.messagesSubject.asObservable();

  /** Current conversation mode. */
  private modeSubject = new BehaviorSubject<string>('chat');
  mode$: Observable<string> = this.modeSubject.asObservable();

  /** Loading state. */
  private loadingSubject = new BehaviorSubject<boolean>(false);
  loading$: Observable<boolean> = this.loadingSubject.asObservable();

  /** Error state. */
  private errorSubject = new BehaviorSubject<string | null>(null);
  error$: Observable<string | null> = this.errorSubject.asObservable();

  /** Active challenge data. */
  private challengeSubject = new BehaviorSubject<ChallengeData | null>(null);
  challenge$: Observable<ChallengeData | null> =
    this.challengeSubject.asObservable();

  /** Skill scores. */
  private scoresSubject = new BehaviorSubject<SkillScore[]>([]);
  scores$: Observable<SkillScore[]> = this.scoresSubject.asObservable();

  /** Analysis result. */
  private analysisSubject = new BehaviorSubject<AnalysisResult | null>(null);
  analysis$: Observable<AnalysisResult | null> =
    this.analysisSubject.asObservable();

  /** Generated roadmap. */
  private roadmapSubject = new BehaviorSubject<Roadmap | null>(null);
  roadmap$: Observable<Roadmap | null> = this.roadmapSubject.asObservable();

  /** Session ID. */
  private _sessionId: string;

  constructor(private api: ApiService) {
    this._sessionId = this.getOrCreateSessionId();
  }

  get sessionId(): string {
    return this._sessionId;
  }

  /**
   * Send a user message and process the AI response.
   */
  sendMessage(text: string, mode: 'chat' | 'challenge_response' = 'chat'): void {
    if (!text.trim() || this.loadingSubject.getValue()) return;

    this.errorSubject.next(null);

    // Add user message to the stream
    const userMessage: ChatMessage = {
      id: this.generateId(),
      role: 'user',
      content: text,
      timestamp: new Date(),
      mode,
    };
    this.addMessage(userMessage);

    // Build request
    const request: ChatRequest = {
      session_id: this._sessionId,
      message: text,
      mode,
    };

    this.loadingSubject.next(true);

    this.api
      .sendMessage(request)
      .pipe(finalize(() => this.loadingSubject.next(false)))
      .subscribe({
        next: (response: ChatResponse) => {
          this.processResponse(response);
        },
        error: (err: Error) => {
          this.errorSubject.next(err.message);
          const errorMessage: ChatMessage = {
            id: this.generateId(),
            role: 'system',
            content: `⚠️ ${err.message}`,
            timestamp: new Date(),
          };
          this.addMessage(errorMessage);
        },
      });
  }

  /**
   * Submit a challenge response.
   */
  submitChallengeResponse(answer: string): void {
    this.sendMessage(answer, 'challenge_response');
  }

  /**
   * Reset the chat session.
   */
  resetSession(): void {
    this._sessionId = this.generateSessionId();
    this.saveSessionId(this._sessionId);
    this.messagesSubject.next([]);
    this.modeSubject.next('chat');
    this.challengeSubject.next(null);
    this.scoresSubject.next([]);
    this.analysisSubject.next(null);
    this.roadmapSubject.next(null);
    this.errorSubject.next(null);
  }

  /**
   * Process a response from the AI backend.
   */
  private processResponse(response: ChatResponse): void {
    const aiMessage: ChatMessage = {
      id: this.generateId(),
      role: 'assistant',
      content: response.message,
      timestamp: new Date(),
      mode: response.mode,
      challengeData: response.challenge_data,
      skillScores: response.skill_scores,
      analysis: response.analysis,
      roadmap: response.roadmap,
    };

    this.addMessage(aiMessage);
    this.modeSubject.next(response.mode);

    // Update state based on mode
    if (response.challenge_data) {
      this.challengeSubject.next(response.challenge_data);
    }

    if (response.skill_scores) {
      const current = this.scoresSubject.getValue();
      this.scoresSubject.next([...current, ...response.skill_scores]);
    }

    if (response.analysis) {
      this.analysisSubject.next(response.analysis);
    }

    if (response.roadmap) {
      this.roadmapSubject.next(response.roadmap);
    }
  }

  private addMessage(message: ChatMessage): void {
    const current = this.messagesSubject.getValue();
    this.messagesSubject.next([...current, message]);
  }

  private getOrCreateSessionId(): string {
    if (typeof window !== 'undefined' && window.localStorage) {
      const stored = localStorage.getItem('careercompass_session_id');
      if (stored) return stored;
    }
    const newId = this.generateSessionId();
    this.saveSessionId(newId);
    return newId;
  }

  private generateSessionId(): string {
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substring(2, 8);
    return `cc_${timestamp}_${random}`;
  }

  private saveSessionId(id: string): void {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('careercompass_session_id', id);
    }
  }

  private generateId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;
  }
}
