import {
  Component,
  OnInit,
  OnDestroy,
  ViewChild,
  ElementRef,
  AfterViewChecked,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { ChatService } from '../../services/chat.service';
import { SeoService } from '../../services/seo.service';
import { ChallengeCardComponent } from '../challenge-card/challenge-card.component';
import { ChatMessage } from '../../models/interfaces';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule, ChallengeCardComponent],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.css',
})
export class ChatComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  @ViewChild('messageInput') private messageInput!: ElementRef;

  messages: ChatMessage[] = [];
  currentMessage = '';
  isLoading = false;
  currentMode = 'chat';
  error: string | null = null;

  private subs: Subscription[] = [];
  private shouldScroll = false;

  constructor(
    private chatService: ChatService,
    private seo: SeoService
  ) {}

  ngOnInit(): void {
    this.seo.updateForChat();

    this.subs.push(
      this.chatService.messages$.subscribe((msgs) => {
        this.messages = msgs;
        this.shouldScroll = true;
      }),
      this.chatService.loading$.subscribe((loading) => {
        this.isLoading = loading;
      }),
      this.chatService.mode$.subscribe((mode) => {
        this.currentMode = mode;
      }),
      this.chatService.error$.subscribe((err) => {
        this.error = err;
      })
    );
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  ngOnDestroy(): void {
    this.subs.forEach((s) => s.unsubscribe());
  }

  sendMessage(): void {
    if (!this.currentMessage.trim() || this.isLoading) return;
    this.chatService.sendMessage(this.currentMessage.trim());
    this.currentMessage = '';
  }

  onKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  onChallengeSubmit(answer: string): void {
    this.chatService.submitChallengeResponse(answer);
  }

  resetChat(): void {
    this.chatService.resetSession();
  }

  trackByMessageId(_index: number, message: ChatMessage): string {
    return message.id;
  }

  private scrollToBottom(): void {
    try {
      if (this.messagesContainer) {
        const el = this.messagesContainer.nativeElement;
        el.scrollTop = el.scrollHeight;
      }
    } catch (err) {
      // noop
    }
  }
}
