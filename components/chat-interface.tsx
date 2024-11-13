'use client'

import { useState } from 'react'
import { Send, Plus, X } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"

type Message = {
  role: 'user' | 'ai'
  content: string
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isGDriveConnected, setIsGDriveConnected] = useState(false)
  const [isGDriveDialogOpen, setIsGDriveDialogOpen] = useState(false)
  const [isEmergeCohortEnabled, setIsEmergeCohortEnabled] = useState(false)

  const handleSend = async () => {
    if (input.trim()) {
      const userMessage = { role: 'user', content: input }
      setMessages([...messages, userMessage])
      setInput('')

      try {
        const response = await fetch('http://localhost:8000/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ messages: [...messages, userMessage] }),
        })

        if (!response.ok) {
          throw new Error('Failed to get response from server')
        }

        const data = await response.json()
        const aiMessage = { role: 'ai', content: data.response }
        setMessages((prevMessages) => [...prevMessages, aiMessage])
      } catch (error) {
        console.error('Error:', error)
        const errorMessage = { role: 'ai', content: 'Sorry, there was an error processing your request.' }
        setMessages((prevMessages) => [...prevMessages, errorMessage])
      }
    }
  }

  const handleGDriveConnect = () => {
    setIsGDriveDialogOpen(true)
  }

  const handleGDriveDisconnect = () => {
    setIsGDriveConnected(false)
  }

  const handleEmergeCohortToggle = () => {
    setIsEmergeCohortEnabled(!isEmergeCohortEnabled)
    setMessages([])
  }

  return (
    <div className="flex h-screen">
      <aside className="w-64 bg-gray-100 p-4 flex flex-col">
        <h2 className="text-xl font-bold mb-4">Options</h2>
        {isGDriveConnected ? (
          <Button variant="outline" onClick={handleGDriveDisconnect} className="mb-2">
            <X className="mr-2 h-4 w-4" /> Disconnect Google Drive
          </Button>
        ) : (
          <Button variant="outline" onClick={handleGDriveConnect} className="mb-2">
            <Plus className="mr-2 h-4 w-4" /> Add Google Drive
          </Button>
        )}
        <div className="flex items-center space-x-2 mt-4">
          <Switch
            id="emerge-cohort"
            checked={isEmergeCohortEnabled}
            onCheckedChange={handleEmergeCohortToggle}
          />
          <Label htmlFor="emerge-cohort">Emerge Cohort 45 Context</Label>
        </div>
        {isEmergeCohortEnabled && (
          <p className="text-sm text-muted-foreground mt-2">
            Emerge Cohort 45 context is enabled. The AI will now include information about this program in its responses.
          </p>
        )}
      </aside>
      <div className="flex-1 flex flex-col">
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
      <Dialog open={isGDriveDialogOpen} onOpenChange={setIsGDriveDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Connect Google Drive</DialogTitle>
            <DialogDescription>
              Click the button below to connect your Google Drive account.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button onClick={() => {
              setIsGDriveConnected(true)
              setIsGDriveDialogOpen(false)
            }}>
              Connect Google Drive
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}