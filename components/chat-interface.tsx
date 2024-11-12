'use client'

import { useState } from 'react'
import { Send } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"

interface Message {
  role: 'user' | 'ai'
  content: string
}

const mockResponses: { [key: string]: string } = {
  "what is the name of our cohort?": "The name of our cohort is Women of Grace and Grit.",
  "hello": "Hello! How can I assist you today?",
  "who are you?": "I'm an AI assistant created to help answer questions about the Women of Grace and Grit cohort.",
  "what is the purpose of this cohort?": "The Women of Grace and Grit cohort is designed to empower and support women in their personal and professional growth.",
  "when did the cohort start?": "The cohort started in early 2023. For the exact date, please check with the program coordinators.",
}

export function ChatInterfaceComponent() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')

  const getAIResponse = (userMessage: string): string => {
    const lowerCaseMessage = userMessage.toLowerCase().trim()
    for (const [key, value] of Object.entries(mockResponses)) {
      if (lowerCaseMessage.includes(key)) {
        return value
      }
    }
    return "I'm sorry, I don't have specific information about that. Is there anything else I can help you with regarding the Women of Grace and Grit cohort?"
  }

  const handleSend = () => {
    if (input.trim()) {
      const userMessage: Message = { role: 'user', content: input }
      const aiMessage: Message = { role: 'ai', content: getAIResponse(input) }
      setMessages([...messages, userMessage, aiMessage])
      setInput('')
    }
  }

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto">
      <ScrollArea className="flex-1 p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] p-3 rounded-lg ${
                message.role === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted'
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
      </ScrollArea>
      <div className="border-t p-4">
        <div className="flex space-x-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message here..."
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          />
          <Button onClick={handleSend}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}