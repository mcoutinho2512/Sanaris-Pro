'use client';

import { useState, useEffect, useRef } from 'react';
import { MessageSquare, Send, Users, Hash, Plus, ArrowLeft, ExternalLink, X, UserPlus } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface Channel {
  id: string;
  name: string;
  channel_type: string;
  sector?: string;
  unread_count: number;
  last_message?: string;
}

interface Message {
  id: string;
  sender: {
    id: string;
    full_name: string;
    email: string;
  };
  content: string;
  created_at: string;
  is_edited: boolean;
}

interface UserOption {
  id: string;
  full_name: string;
  email: string;
}

export default function ChatPage() {
  const router = useRouter();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [showNewChannelModal, setShowNewChannelModal] = useState(false);
  const [availableUsers, setAvailableUsers] = useState<UserOption[]>([]);
  const [newChannelName, setNewChannelName] = useState('');
  const [newChannelType, setNewChannelType] = useState<'group' | 'direct'>('group');
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadChannels();
    loadCurrentUser();
    loadUsers();
  }, []);

  useEffect(() => {
    if (selectedChannel && currentUser) {
      connectWebSocket();
      loadMessages(selectedChannel.id);
    }
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [selectedChannel, currentUser]);

  const loadCurrentUser = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8888/api/v1/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentUser(data);
        console.log('✅ Usuário carregado:', data.full_name);
      }
    } catch (error) {
      console.error('Erro ao carregar usuário:', error);
    }
  };

  const loadUsers = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8888/api/v1/users/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setAvailableUsers(data);
        console.log('✅ Usuários carregados:', data.length);
      } else {
        console.error('❌ Erro ao carregar usuários:', response.status);
      }
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
    }
  };

  const loadChannels = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8888/api/chat/channels', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setChannels(data);
        if (data.length > 0 && !selectedChannel) {
          setSelectedChannel(data[0]);
        }
      }
    } catch (error) {
      console.error('Erro ao carregar canais:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadMessages = async (channelId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8888/api/chat/channels/${channelId}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (error) {
      console.error('Erro ao carregar mensagens:', error);
    }
  };

  const connectWebSocket = () => {
    if (!currentUser) return;

    const ws = new WebSocket(`ws://localhost:8888/api/chat/ws/${currentUser.id}`);
    
    ws.onopen = () => {
      console.log('✅ WebSocket conectado');
      if (selectedChannel) {
        ws.send(JSON.stringify({
          type: 'subscribe',
          channel_id: selectedChannel.id
        }));
      }
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'message') {
        setMessages(prev => [...prev, data.data]);
      }
    };

    ws.onerror = () => {
      // Silenciar
    };

    ws.onclose = () => {
      console.log('WebSocket desconectado');
    };

    wsRef.current = ws;
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedChannel) {
      console.log('❌ Mensagem vazia ou canal não selecionado');
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      
      const payload = {
        channel_id: selectedChannel.id,
        content: newMessage.trim(),
        message_type: 'text'
      };
      
      console.log('📤 Enviando:', payload);
      
      const response = await fetch('http://localhost:8888/api/chat/messages', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        console.log('✅ Mensagem enviada!');
        setNewMessage('');
      } else {
        const errorText = await response.text();
        console.error('❌ Erro ao enviar:', response.status, errorText);
        alert('Erro ao enviar mensagem. Veja o console.');
      }
    } catch (error) {
      console.error('❌ Erro:', error);
      alert('Erro ao enviar mensagem!');
    }
  };

  const createChannel = async () => {
    if (!newChannelName.trim()) {
      alert('Digite um nome para o canal!');
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      
      const payload = {
        name: newChannelName,
        description: `Canal ${newChannelName}`,
        channel_type: newChannelType,
        sector: newChannelType === 'group' ? 'Geral' : undefined,
        participant_ids: selectedUsers
      };
      
      console.log('📤 Criando canal:', payload);
      
      const response = await fetch('http://localhost:8888/api/chat/channels', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        console.log('✅ Canal criado!');
        setShowNewChannelModal(false);
        setNewChannelName('');
        setSelectedUsers([]);
        loadChannels();
      } else {
        const errorText = await response.text();
        console.error('❌ Erro ao criar canal:', response.status, errorText);
        alert('Erro ao criar canal. Veja o console.');
      }
    } catch (error) {
      console.error('❌ Erro:', error);
      alert('Erro ao criar canal!');
    }
  };

  const openInNewWindow = () => {
    window.open('/chat', 'Chat', 'width=1200,height=800');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando chat...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-bold text-gray-900">Chat</h2>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={openInNewWindow}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Abrir em nova janela"
              >
                <ExternalLink className="w-5 h-5 text-gray-600" />
              </button>
              <button
                onClick={() => setShowNewChannelModal(true)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Novo canal/conversa"
              >
                <Plus className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          </div>
          <button
            onClick={() => router.push('/')}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Voltar ao sistema
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {channels.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              <MessageSquare className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>Nenhum canal encontrado</p>
              <button
                onClick={() => setShowNewChannelModal(true)}
                className="mt-2 text-blue-600 hover:underline text-sm"
              >
                Criar primeiro canal
              </button>
            </div>
          ) : (
            channels.map((channel) => (
              <button
                key={channel.id}
                onClick={() => setSelectedChannel(channel)}
                className={`w-full p-4 text-left hover:bg-gray-50 border-b border-gray-100 transition-colors ${
                  selectedChannel?.id === channel.id ? 'bg-blue-50 border-l-4 border-l-blue-600' : ''
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    {channel.channel_type === 'direct' ? (
                      <Users className="w-4 h-4 text-gray-400" />
                    ) : (
                      <Hash className="w-4 h-4 text-gray-400" />
                    )}
                    <span className="font-semibold text-gray-900">{channel.name}</span>
                  </div>
                  {channel.unread_count > 0 && (
                    <span className="bg-blue-600 text-white text-xs font-bold px-2 py-1 rounded-full">
                      {channel.unread_count}
                    </span>
                  )}
                </div>
                {channel.last_message && (
                  <p className="text-sm text-gray-500 truncate">{channel.last_message}</p>
                )}
                {channel.sector && (
                  <span className="inline-block mt-1 text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                    {channel.sector}
                  </span>
                )}
              </button>
            ))
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        {selectedChannel ? (
          <>
            <div className="bg-white border-b border-gray-200 p-4">
              <h3 className="text-lg font-bold text-gray-900">{selectedChannel.name}</h3>
              {selectedChannel.sector && (
                <p className="text-sm text-gray-500">{selectedChannel.sector}</p>
              )}
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 ? (
                <div className="text-center text-gray-400 mt-20">
                  <MessageSquare className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <p>Nenhuma mensagem ainda</p>
                  <p className="text-sm">Seja o primeiro a enviar uma mensagem!</p>
                </div>
              ) : (
                messages.map((message) => {
                  const isOwnMessage = currentUser && message.sender.id === currentUser.id;
                  
                  return (
                    <div
                      key={message.id}
                      className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[70%]`}>
                        {!isOwnMessage && (
                          <p className="text-xs font-semibold text-gray-700 mb-1 px-1">
                            {message.sender.full_name}
                          </p>
                        )}
                        <div
                          className={`rounded-2xl px-4 py-2 ${
                            isOwnMessage
                              ? 'bg-blue-600 text-white'
                              : 'bg-white border border-gray-200 text-gray-900'
                          }`}
                        >
                          <p className="whitespace-pre-wrap break-words">{message.content}</p>
                          <span className={`text-xs ${isOwnMessage ? 'text-blue-100' : 'text-gray-400'}`}>
                            {formatTime(message.created_at)}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="bg-white border-t border-gray-200 p-4">
              <div className="flex items-end gap-2">
                <textarea
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Digite sua mensagem..."
                  className="flex-1 resize-none border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent min-h-[48px] max-h-32"
                  rows={1}
                />
                <button
                  onClick={sendMessage}
                  disabled={!newMessage.trim()}
                  className="bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <MessageSquare className="w-20 h-20 mx-auto mb-4 text-gray-300" />
              <p className="text-lg">Selecione um canal para começar</p>
            </div>
          </div>
        )}
      </div>

      {showNewChannelModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-900">Novo Canal/Conversa</h3>
              <button
                onClick={() => setShowNewChannelModal(false)}
                className="p-1 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo
                </label>
                <div className="flex gap-2">
                  <button
                    onClick={() => setNewChannelType('group')}
                    className={`flex-1 py-2 px-4 rounded-lg border-2 transition-colors ${
                      newChannelType === 'group'
                        ? 'border-blue-600 bg-blue-50 text-blue-600'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Hash className="w-5 h-5 mx-auto mb-1" />
                    Grupo
                  </button>
                  <button
                    onClick={() => setNewChannelType('direct')}
                    className={`flex-1 py-2 px-4 rounded-lg border-2 transition-colors ${
                      newChannelType === 'direct'
                        ? 'border-blue-600 bg-blue-50 text-blue-600'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Users className="w-5 h-5 mx-auto mb-1" />
                    Direto
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nome
                </label>
                <input
                  type="text"
                  value={newChannelName}
                  onChange={(e) => setNewChannelName(e.target.value)}
                  placeholder="Ex: Equipe Médica"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <UserPlus className="w-4 h-4 inline mr-1" />
                  Adicionar usuários ({availableUsers.length} disponíveis)
                </label>
                <div className="max-h-48 overflow-y-auto border border-gray-200 rounded-lg p-2">
                  {availableUsers.filter(u => u.id !== currentUser?.id).map((user) => (
                    <label
                      key={user.id}
                      className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={selectedUsers.includes(user.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedUsers([...selectedUsers, user.id]);
                          } else {
                            setSelectedUsers(selectedUsers.filter(id => id !== user.id));
                          }
                        }}
                        className="rounded border-gray-300"
                      />
                      <div>
                        <p className="text-sm font-medium">{user.full_name}</p>
                        <p className="text-xs text-gray-500">{user.email}</p>
                      </div>
                    </label>
                  ))}
                  {availableUsers.filter(u => u.id !== currentUser?.id).length === 0 && (
                    <p className="text-sm text-gray-500 text-center py-4">Nenhum outro usuário disponível</p>
                  )}
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => setShowNewChannelModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={createChannel}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Criar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
