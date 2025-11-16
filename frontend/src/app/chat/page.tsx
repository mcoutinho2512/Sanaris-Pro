'use client';

import { useState, useEffect, useRef } from 'react';
import { MessageSquare, Send, Users, Hash, Plus, ArrowLeft, ExternalLink, X, UserPlus, Settings, Trash2, UserMinus, Paperclip, Image as ImageIcon, File } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface Channel {
  id: string;
  name: string;
  channel_type: string;
  sector?: string;
  unread_count: number;
  last_message?: string;
  created_by_id: string;
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
  message_type: string;
  file_url?: string;
  file_name?: string;
}

interface UserOption {
  id: string;
  full_name: string;
  email: string;
}

interface Participant {
  id: string;
  full_name: string;
  email: string;
  role: string;
  joined_at: string;
}

export default function ChatPage() {
  const router = useRouter();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState<any>(null);
  
  // Modais
  const [showNewChannelModal, setShowNewChannelModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showParticipantsModal, setShowParticipantsModal] = useState(false);
  
  // Dados dos modais
  const [availableUsers, setAvailableUsers] = useState<UserOption[]>([]);
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [newChannelName, setNewChannelName] = useState('');
  const [newChannelType, setNewChannelType] = useState<'group' | 'direct'>('group');
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  
  // Upload
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
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
      loadParticipants(selectedChannel.id);
    }
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [selectedChannel, currentUser]);

  const loadCurrentUser = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8888/api/v1/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentUser(data);
      }
    } catch (error) {
      console.error('Erro ao carregar usuário:', error);
    }
  };

  const loadUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8888/api/v1/users-management/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setAvailableUsers(data);
      }
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
    }
  };

  const loadChannels = async () => {
    try {
      const token = localStorage.getItem('token');
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
      const token = localStorage.getItem('token');
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

  const loadParticipants = async (channelId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8888/api/chat/channels/${channelId}/participants`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setParticipants(data);
      }
    } catch (error) {
      console.error('Erro ao carregar participantes:', error);
    }
  };

  const connectWebSocket = () => {
    if (!currentUser) return;

    const ws = new WebSocket(`ws://localhost:8888/api/chat/ws/${currentUser.id}`);
    
    ws.onopen = () => {
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

    ws.onerror = () => {};
    ws.onclose = () => {};

    wsRef.current = ws;
  };

  const uploadFile = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8888/api/files/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('Erro no upload:', error);
    }
    return null;
  };

  const sendMessage = async () => {
    if ((!newMessage.trim() && !selectedFile) || !selectedChannel) return;

    setIsUploading(true);

    try {
      const token = localStorage.getItem('token');
      let fileData = null;

      // Upload do arquivo se houver
      if (selectedFile) {
        fileData = await uploadFile(selectedFile);
        if (!fileData) {
          alert('Erro ao fazer upload do arquivo');
          setIsUploading(false);
          return;
        }
      }

      const payload: any = {
        channel_id: selectedChannel.id,
        content: newMessage.trim() || fileData?.filename || 'Arquivo',
        message_type: selectedFile ? (selectedFile.type.startsWith('image/') ? 'image' : 'file') : 'text'
      };

      if (fileData) {
        payload.file_url = fileData.url;
        payload.file_name = fileData.filename;
      }
      
      const response = await fetch('http://localhost:8888/api/chat/messages', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        setNewMessage('');
        setSelectedFile(null);
      }
    } catch (error) {
      console.error('Erro ao enviar:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const createChannel = async () => {
    // Validação: precisa ter pelo menos 1 usuário
    if (selectedUsers.length === 0) {
      alert('Selecione pelo menos um usuário!');
      return;
    }

    // Se for grupo (2+ usuários), nome é obrigatório
    if (selectedUsers.length > 1 && !newChannelName.trim()) {
      alert('Digite um nome para o grupo!');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      
      // Se for chat direto (1 usuário), usar nome do usuário
      let channelName = newChannelName.trim();
      let channelType = newChannelType;
      
      if (selectedUsers.length === 1) {
        const selectedUser = availableUsers.find(u => u.id === selectedUsers[0]);
        channelName = selectedUser?.full_name || 'Chat Direto';
        channelType = 'direct';
      }
      
      const response = await fetch('http://localhost:8888/api/chat/channels', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: channelName,
          description: selectedUsers.length === 1 ? `Chat com ${channelName}` : `Grupo ${channelName}`,
          channel_type: channelType,
          sector: channelType === 'group' ? 'Geral' : undefined,
          participant_ids: selectedUsers
        })
      });
      
      if (response.ok) {
        const newChannel = await response.json();
        setShowNewChannelModal(false);
        setNewChannelName('');
        setSelectedUsers([]);
        await loadChannels();
        setSelectedChannel(newChannel);
        alert(selectedUsers.length === 1 ? 'Chat iniciado!' : 'Grupo criado com sucesso!');
      } else {
        const error = await response.json();
        alert(error.detail || 'Erro ao criar canal');
      }
    } catch (error) {
      console.error('Erro ao criar canal:', error);
      alert('Erro ao criar canal. Verifique sua conexão.');
    }
  };


  const deleteChannel = async () => {
    if (!selectedChannel) return;
    if (!confirm('Deseja realmente excluir este canal?')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8888/api/chat/channels/${selectedChannel.id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        alert('Canal excluído!');
        setShowSettingsModal(false);
        setSelectedChannel(null);
        loadChannels();
      }
    } catch (error) {
      console.error('Erro ao excluir:', error);
    }
  };

  const addParticipant = async (userId: string) => {
    if (!selectedChannel) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8888/api/chat/channels/${selectedChannel.id}/participants`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId })
      });

      if (response.ok) {
        loadParticipants(selectedChannel.id);
        loadUsers();
      }
    } catch (error) {
      console.error('Erro ao adicionar:', error);
    }
  };

  const removeParticipant = async (userId: string) => {
    if (!selectedChannel) return;
    if (!confirm('Remover este participante?')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8888/api/chat/channels/${selectedChannel.id}/participants/${userId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        loadParticipants(selectedChannel.id);
      }
    } catch (error) {
      console.error('Erro ao remover:', error);
    }
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
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-bold text-gray-900">Chat</h2>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => window.open('/chat', 'Chat', 'width=1200,height=800')}
                className="p-2 hover:bg-gray-100 rounded-lg"
                title="Abrir em nova janela"
              >
                <ExternalLink className="w-5 h-5 text-gray-600" />
              </button>
              <button
                onClick={() => setShowNewChannelModal(true)}
                className="p-2 hover:bg-gray-100 rounded-lg"
                title="Novo canal"
              >
                <Plus className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          </div>
          <button
            onClick={() => router.push('/')}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeft className="w-4 h-4" />
            Voltar ao sistema
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {channels.map((channel) => (
            <button
              key={channel.id}
              onClick={() => setSelectedChannel(channel)}
              className={`w-full p-4 text-left hover:bg-gray-50 border-b border-gray-100 ${
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
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Área de Mensagens */}
      <div className="flex-1 flex flex-col">
        {selectedChannel ? (
          <>
            <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-gray-900">{selectedChannel.name}</h3>
              </div>
              <button
                onClick={() => setShowSettingsModal(true)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <Settings className="w-5 h-5 text-gray-600" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map((message) => {
                const isOwnMessage = currentUser && message.sender.id === currentUser.id;
                
                return (
                  <div key={message.id} className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}>
                    <div className="max-w-[70%]">
                      {!isOwnMessage && (
                        <p className="text-xs font-semibold text-gray-700 mb-1 px-1">
                          {message.sender.full_name}
                        </p>
                      )}
                      <div className={`rounded-2xl px-4 py-2 ${
                        isOwnMessage ? 'bg-blue-600 text-white' : 'bg-white border border-gray-200 text-gray-900'
                      }`}>
                        {message.message_type === 'image' && message.file_url && (
                          <img src={`http://localhost:8888${message.file_url}`} alt={message.file_name} className="max-w-full rounded mb-2" />
                        )}
                        {message.message_type === 'file' && message.file_url && (
                          <a 
                            href={`http://localhost:8888${message.file_url}`} 
                            target="_blank" 
                            download
                            className={`flex items-center gap-2 p-2 rounded hover:opacity-80 mb-2 ${
                              isOwnMessage ? 'bg-blue-700' : 'bg-gray-100'
                            }`}
                          >
                            <File className={`w-5 h-5 ${isOwnMessage ? 'text-white' : 'text-blue-600'}`} />
                            <span className={isOwnMessage ? 'text-white' : 'text-blue-600'}>
                              {message.file_name || 'Arquivo'}
                            </span>
                          </a>
                        )}
                        <p className="whitespace-pre-wrap break-words">{message.content}</p>
                        <span className={`text-xs ${isOwnMessage ? 'text-blue-100' : 'text-gray-400'}`}>
                          {formatTime(message.created_at)}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            <div className="bg-white border-t border-gray-200 p-4">
              {selectedFile && (
                <div className="flex items-center gap-2 mb-2 p-2 bg-blue-50 rounded">
                  <File className="w-4 h-4 text-blue-600" />
                  <span className="text-sm flex-1">{selectedFile.name}</span>
                  <button onClick={() => setSelectedFile(null)} className="text-red-600">
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
              <div className="flex items-end gap-2">
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="p-3 hover:bg-gray-100 rounded-xl"
                  title="Anexar arquivo"
                >
                  <Paperclip className="w-5 h-5 text-gray-600" />
                </button>
                <textarea
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Digite sua mensagem..."
                  className="flex-1 resize-none border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-600 min-h-[48px] max-h-32"
                  rows={1}
                />
                <button
                  onClick={sendMessage}
                  disabled={isUploading || (!newMessage.trim() && !selectedFile)}
                  className="bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 disabled:opacity-50"
                >
                  {isUploading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <MessageSquare className="w-20 h-20 text-gray-300" />
          </div>
        )}
      </div>

      {/* MODAL NOVO CANAL */}
      {showNewChannelModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold">Novo Canal</h3>
              <button onClick={() => setShowNewChannelModal(false)}>
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Tipo</label>
                <div className="flex gap-2">
                  <button
                    onClick={() => setNewChannelType('group')}
                    className={`flex-1 py-2 px-4 rounded-lg border-2 ${
                      newChannelType === 'group' ? 'border-blue-600 bg-blue-50' : 'border-gray-200'
                    }`}
                  >
                    <Hash className="w-5 h-5 mx-auto mb-1" />
                    Grupo
                  </button>
                  <button
                    onClick={() => setNewChannelType('direct')}
                    className={`flex-1 py-2 px-4 rounded-lg border-2 ${
                      newChannelType === 'direct' ? 'border-blue-600 bg-blue-50' : 'border-gray-200'
                    }`}
                  >
                    <Users className="w-5 h-5 mx-auto mb-1" />
                    Direto
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Nome</label>
                <input
                  type="text"
                  value={newChannelName}
                  onChange={(e) => setNewChannelName(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-600"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Adicionar usuários ({availableUsers.length} disponíveis)
                </label>
                <div className="max-h-48 overflow-y-auto border rounded-lg p-2">
                  {availableUsers.filter(u => u.id !== currentUser?.id).map((user) => (
                    <label key={user.id} className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer">
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
                      />
                      <div>
                        <p className="text-sm font-medium">{user.full_name}</p>
                        <p className="text-xs text-gray-500">{user.email}</p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowNewChannelModal(false)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={createChannel}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Criar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL CONFIGURAÇÕES */}
      {showSettingsModal && selectedChannel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold">Configurações do Canal</h3>
              <button onClick={() => setShowSettingsModal(false)}>
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-2">
              <button
                onClick={() => {
                  setShowSettingsModal(false);
                  setShowParticipantsModal(true);
                }}
                className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 rounded-lg"
              >
                <Users className="w-5 h-5 text-gray-600" />
                <span>Gerenciar Participantes</span>
              </button>
              {currentUser && selectedChannel.created_by_id === currentUser.id && (
                <button
                  onClick={deleteChannel}
                  className="w-full flex items-center gap-3 px-4 py-3 hover:bg-red-50 rounded-lg text-red-600"
                >
                  <Trash2 className="w-5 h-5" />
                  <span>Excluir Canal</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* MODAL PARTICIPANTES */}
      {showParticipantsModal && selectedChannel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold">Participantes</h3>
              <button onClick={() => setShowParticipantsModal(false)}>
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="mb-4">
              <h4 className="font-semibold mb-2">Adicionar Participante</h4>
              <div className="max-h-48 overflow-y-auto border rounded-lg p-2">
                {availableUsers
                  .filter(u => u.id !== currentUser?.id && !participants.find(p => p.id === u.id))
                  .map((user) => (
                    <div key={user.id} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                      <div>
                        <p className="text-sm font-medium">{user.full_name}</p>
                        <p className="text-xs text-gray-500">{user.email}</p>
                      </div>
                      <button
                        onClick={() => addParticipant(user.id)}
                        className="p-1 hover:bg-blue-100 rounded text-blue-600"
                      >
                        <UserPlus className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Participantes Atuais ({participants.length})</h4>
              <div className="space-y-2">
                {participants.map((participant) => (
                  <div key={participant.id} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                    <div>
                      <p className="text-sm font-medium">{participant.full_name}</p>
                      <p className="text-xs text-gray-500">{participant.email}</p>
                    </div>
                    {currentUser && participant.id !== currentUser.id && (
                      <button
                        onClick={() => removeParticipant(participant.id)}
                        className="p-1 hover:bg-red-100 rounded text-red-600"
                      >
                        <UserMinus className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
