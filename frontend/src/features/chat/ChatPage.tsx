import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User as UserIcon, Sparkles, AlertTriangle, CheckCircle2, Wifi } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { chatApi } from '@/api'
import { AgentBadge } from './components/AgentBadge'
import { ConfidenceBar } from './components/ConfidenceBar'
import { ExplainabilityPanel } from './components/ExplainabilityPanel'

// ── Types ─────────────────────────────────────────────────────────────────────

interface TimelineStep {
  step: string
  agent: string
  timestamp: string
  details: string
}

interface EscalationInfo {
  needed: boolean
  ticket_number: string | null
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  agentsUsed?: string[]
  confidenceScore?: number
  escalation?: EscalationInfo
  timeline?: TimelineStep[]
  isLoading?: boolean
}

// ── Suggested prompts ─────────────────────────────────────────────────────────

const SUGGESTED_PROMPTS = [
  '📦 Where is my latest order?',
  '💳 I want to request a refund',
  '📋 What is your return policy?',
  '🚨 I need to speak to a human agent',
]

// ── Session ID utility ────────────────────────────────────────────────────────

function getOrCreateSessionId(): string {
  const key = 'chat_session_id'
  let id = sessionStorage.getItem(key)
  if (!id) {
    id = `sess-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
    sessionStorage.setItem(key, id)
  }
  return id
}

// ── Component ─────────────────────────────────────────────────────────────────

export function ChatPage() {
  const { user } = useAuthStore()
  const sessionId = useRef<string>(getOrCreateSessionId())
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const firstName = user?.full_name?.split(' ')[0] ?? 'there'

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Hi ${firstName}! I'm your AI support agent powered by LangGraph multi-agent orchestration. I can help you track orders, process refunds, and answer policy questions.\n\nHow can I help you today?`,
    },
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  const handleSend = async (text?: string) => {
    const messageText = (text ?? input).trim()
    if (!messageText || isTyping) return

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: messageText,
    }

    const loadingId = `loading-${Date.now()}`
    setMessages(prev => [...prev, userMsg, { id: loadingId, role: 'assistant', content: '', isLoading: true }])
    setInput('')
    setIsTyping(true)

    try {
      const res = await chatApi.sendMessage({
        session_id: sessionId.current,
        message: messageText,
      })

      const data = res.data as {
        message: string
        session_id: string
        agents_used: string[]
        confidence_score: number
        escalation: EscalationInfo
        timeline: TimelineStep[]
        message_id: string
      }

      const aiMsg: Message = {
        id: data.message_id ?? `ai-${Date.now()}`,
        role: 'assistant',
        content: data.message,
        agentsUsed: data.agents_used ?? [],
        confidenceScore: data.confidence_score ?? 0,
        escalation: data.escalation,
        timeline: data.timeline ?? [],
      }

      setMessages(prev => prev.filter(m => m.id !== loadingId).concat(aiMsg))
    } catch {
      setMessages(prev =>
        prev
          .filter(m => m.id !== loadingId)
          .concat({
            id: `err-${Date.now()}`,
            role: 'assistant',
            content: '⚠️ I encountered a connection error. Please check your network and try again.',
          })
      )
    } finally {
      setIsTyping(false)
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="h-[calc(100vh-8rem)] max-w-4xl mx-auto flex flex-col bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">

      {/* ── Header ──────────────────────────────────────────────────────────── */}
      <div className="h-16 border-b border-slate-100 flex items-center justify-between px-6 bg-gradient-to-r from-slate-50 to-violet-50/30 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center shadow-md shadow-violet-500/20">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-slate-800 flex items-center gap-2">
              AI Support Agent
              <span className="px-2 py-0.5 rounded-full bg-violet-100 text-violet-700 text-[10px] font-bold uppercase tracking-wider">
                LangGraph
              </span>
            </h2>
            <p className="text-xs text-slate-500">Multi-agent orchestration • Order • Refund • FAQ • Escalation</p>
          </div>
        </div>

        {/* Live status dot */}
        <div className="flex items-center gap-1.5 text-xs text-emerald-600 font-medium">
          <motion.div
            className="w-2 h-2 rounded-full bg-emerald-500"
            animate={{ opacity: [1, 0.4, 1] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          />
          <Wifi className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Connected</span>
        </div>
      </div>

      {/* ── Messages ────────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gradient-to-b from-white to-slate-50/50">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 12, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
              className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${
                  msg.role === 'assistant'
                    ? 'gradient-primary text-white shadow-md shadow-violet-500/20'
                    : 'bg-slate-100 text-slate-600 border border-slate-200'
                }`}
              >
                {msg.role === 'assistant' ? <Bot className="w-4 h-4" /> : <UserIcon className="w-4 h-4" />}
              </div>

              {/* Bubble + metadata */}
              <div className={`flex flex-col gap-1.5 max-w-[78%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                {/* Bubble */}
                <div
                  className={`rounded-2xl px-5 py-3.5 shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-slate-800 text-white rounded-tr-sm'
                      : 'bg-white border border-slate-200 text-slate-700 rounded-tl-sm'
                  }`}
                >
                  {msg.isLoading ? (
                    <div className="flex items-center gap-1 h-5">
                      {[0, 0.15, 0.3].map((delay, i) => (
                        <motion.div
                          key={i}
                          className="w-2 h-2 rounded-full bg-slate-300"
                          animate={{ y: [0, -6, 0], opacity: [0.5, 1, 0.5] }}
                          transition={{ duration: 0.8, repeat: Infinity, delay, ease: 'easeInOut' }}
                        />
                      ))}
                    </div>
                  ) : (
                    <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                  )}
                </div>

                {/* AI metadata (only for assistant messages with data) */}
                {msg.role === 'assistant' && !msg.isLoading && msg.agentsUsed && (
                  <div className="w-full space-y-2">
                    {/* Agent badges */}
                    {msg.agentsUsed.length > 0 && (
                      <div className="flex flex-wrap gap-1.5">
                        {msg.agentsUsed.map((agent, i) => (
                          <AgentBadge key={agent} agentName={agent} delay={i * 0.08} />
                        ))}
                      </div>
                    )}

                    {/* Confidence bar */}
                    {typeof msg.confidenceScore === 'number' && msg.confidenceScore > 0 && (
                      <ConfidenceBar score={msg.confidenceScore} />
                    )}

                    {/* Escalation notice */}
                    {msg.escalation?.needed && (
                      <motion.div
                        initial={{ opacity: 0, y: 4 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-xl px-3 py-2"
                      >
                        <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                        <div>
                          <p className="text-[12px] font-semibold text-amber-800">Escalated to Human Agent</p>
                          {msg.escalation.ticket_number && (
                            <p className="text-[11px] text-amber-600 mt-0.5">
                              Ticket: <span className="font-mono font-bold">{msg.escalation.ticket_number}</span> — track in your Tickets tab
                            </p>
                          )}
                        </div>
                      </motion.div>
                    )}

                    {/* Resolved badge (non-escalated with agents) */}
                    {!msg.escalation?.needed && msg.agentsUsed.length > 0 && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.4 }}
                        className="flex items-center gap-1.5 text-[11px] text-emerald-600"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Handled by AI agents</span>
                      </motion.div>
                    )}

                    {/* Explainability panel */}
                    {msg.timeline && msg.timeline.length > 0 && (
                      <ExplainabilityPanel timeline={msg.timeline} />
                    )}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* ── Suggested prompts (shown only at start) ──────────────────────────── */}
      {messages.length <= 1 && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="px-6 pb-3 flex flex-wrap gap-2 border-t border-slate-50 bg-white"
        >
          <p className="w-full text-[11px] text-slate-400 font-medium pt-3 pb-1">Suggested questions:</p>
          {SUGGESTED_PROMPTS.map((prompt, i) => (
            <motion.button
              key={prompt}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.06 }}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => handleSend(prompt.replace(/^[^\s]+\s/, ''))}
              className="px-3 py-1.5 rounded-xl text-[12px] font-medium bg-slate-50 border border-slate-200 text-slate-600 hover:bg-violet-50 hover:border-violet-200 hover:text-violet-700 transition-colors"
            >
              {prompt}
            </motion.button>
          ))}
        </motion.div>
      )}

      {/* ── Input area ──────────────────────────────────────────────────────── */}
      <div className="p-4 border-t border-slate-100 bg-white shrink-0">
        <div className="relative flex items-center gap-2 max-w-3xl mx-auto">
          <div className="relative flex-1">
            <input
              ref={inputRef}
              type="text"
              id="chat-input"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message… (Enter to send)"
              disabled={isTyping}
              className="w-full pl-5 pr-12 py-3.5 rounded-2xl border border-slate-200 bg-slate-50 focus:bg-white text-[15px] focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-300 transition-all disabled:opacity-60"
            />
            <Sparkles className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-violet-400 pointer-events-none" />
          </div>
          <motion.button
            id="chat-send-button"
            type="button"
            disabled={!input.trim() || isTyping}
            onClick={() => handleSend()}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="w-12 h-12 rounded-2xl gradient-primary text-white flex items-center justify-center shadow-md shadow-violet-500/20 disabled:opacity-40 disabled:cursor-not-allowed shrink-0 transition-opacity"
          >
            <Send className="w-4 h-4 ml-0.5" />
          </motion.button>
        </div>
        <p className="text-center text-[11px] text-slate-400 mt-2">
          Session: <span className="font-mono">{sessionId.current}</span> · AI may make mistakes — verify critical information
        </p>
      </div>
    </div>
  )
}
