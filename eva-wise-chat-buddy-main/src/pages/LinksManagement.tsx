import React, { useState, useEffect } from 'react';
import { Plus, Search, ExternalLink, RefreshCw, Trash2, Globe, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import chatService, { Link } from '@/services/chatService';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

const LinksManagement: React.FC = () => {
  const [links, setLinks] = useState<Link[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [newUrl, setNewUrl] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [addingLink, setAddingLink] = useState(false);
  const [priority, setPriority] = useState(5);
  const { toast } = useToast();
  const [language, setLanguage] = useState<'ar' | 'en'>('ar');

  useEffect(() => {
    loadLinks();
  }, []);

  const loadLinks = async () => {
    setLoading(true);
    try {
      const response = await chatService.getLinks();
      if (response.success) {
        setLinks(response.links);
      } else {
        toast({
          title: language === 'ar' ? 'خطأ' : 'Error',
          description: response.error || (language === 'ar' ? 'فشل تحميل الروابط' : 'Failed to load links'),
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: language === 'ar' ? 'خطأ' : 'Error',
        description: language === 'ar' ? 'حدث خطأ أثناء تحميل الروابط' : 'An error occurred while loading links',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddLink = async () => {
    if (!newUrl.trim()) {
      toast({
        title: language === 'ar' ? 'خطأ' : 'Error',
        description: language === 'ar' ? 'الرجاء إدخال رابط صحيح' : 'Please enter a valid URL',
        variant: 'destructive',
      });
      return;
    }

    setAddingLink(true);
    try {
      const response = await chatService.addLink(newUrl.trim(), priority, false);
      if (response.success) {
        toast({
          title: language === 'ar' ? 'نجح' : 'Success',
          description: language === 'ar' ? 'تم إضافة الرابط بنجاح' : 'Link added successfully',
        });
        setNewUrl('');
        setIsDialogOpen(false);
        loadLinks();
      } else {
        toast({
          title: language === 'ar' ? 'خطأ' : 'Error',
          description: response.error || (language === 'ar' ? 'فشل إضافة الرابط' : 'Failed to add link'),
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: language === 'ar' ? 'خطأ' : 'Error',
        description: language === 'ar' ? 'حدث خطأ أثناء إضافة الرابط' : 'An error occurred while adding the link',
        variant: 'destructive',
      });
    } finally {
      setAddingLink(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadLinks();
      return;
    }

    setLoading(true);
    try {
      const response = await chatService.searchLinks(searchQuery.trim());
      if (response.success) {
        setLinks(response.results);
      } else {
        toast({
          title: language === 'ar' ? 'خطأ' : 'Error',
          description: response.error || (language === 'ar' ? 'فشل البحث' : 'Search failed'),
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: language === 'ar' ? 'خطأ' : 'Error',
        description: language === 'ar' ? 'حدث خطأ أثناء البحث' : 'An error occurred while searching',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '-';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString(language === 'ar' ? 'ar-EG' : 'en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  const filteredLinks = links.filter((link) => {
    if (!searchQuery.trim()) return true;
    const query = searchQuery.toLowerCase();
    return (
      link.url?.toLowerCase().includes(query) ||
      link.title?.toLowerCase().includes(query) ||
      link.description?.toLowerCase().includes(query) ||
      link.source?.toLowerCase().includes(query)
    );
  });

  return (
    <div className="min-h-screen bg-chat-bg p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-eva-primary to-eva-secondary bg-clip-text text-transparent">
                {language === 'ar' ? 'إدارة الروابط' : 'Links Management'}
              </h1>
              <p className="text-text-secondary mt-2">
                {language === 'ar'
                  ? 'أضف وادير الروابط التي سيتم استخراج البيانات منها'
                  : 'Add and manage links to extract data from'}
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setLanguage(language === 'ar' ? 'en' : 'ar')}
              >
                <Globe className="w-4 h-4 mr-2" />
                {language === 'ar' ? 'EN' : 'عربي'}
              </Button>
              <Button variant="outline" onClick={loadLinks} disabled={loading}>
                <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                {language === 'ar' ? 'تحديث' : 'Refresh'}
              </Button>
            </div>
          </div>

          {/* Search and Add */}
          <div className="flex gap-3">
            <div className="flex-1 flex gap-2">
              <Input
                placeholder={language === 'ar' ? 'ابحث في الروابط...' : 'Search links...'}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="bg-chat-card border-chat-border"
              />
              <Button onClick={handleSearch} disabled={loading}>
                <Search className="w-4 h-4 mr-2" />
                {language === 'ar' ? 'بحث' : 'Search'}
              </Button>
            </div>

            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-gradient-to-r from-eva-primary to-eva-secondary">
                  <Plus className="w-4 h-4 mr-2" />
                  {language === 'ar' ? 'إضافة رابط' : 'Add Link'}
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>
                    {language === 'ar' ? 'إضافة رابط جديد' : 'Add New Link'}
                  </DialogTitle>
                  <DialogDescription>
                    {language === 'ar'
                      ? 'أدخل رابط الموقع الذي تريد استخراج البيانات منه'
                      : 'Enter the URL of the website you want to extract data from'}
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">
                      {language === 'ar' ? 'الرابط (URL)' : 'URL'}
                    </label>
                    <Input
                      placeholder="https://example.com"
                      value={newUrl}
                      onChange={(e) => setNewUrl(e.target.value)}
                      className="bg-chat-card border-chat-border"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">
                      {language === 'ar' ? 'الأولوية' : 'Priority'}
                    </label>
                    <Input
                      type="number"
                      min="1"
                      max="10"
                      value={priority}
                      onChange={(e) => setPriority(parseInt(e.target.value) || 5)}
                      className="bg-chat-card border-chat-border"
                    />
                    <p className="text-xs text-text-muted mt-1">
                      {language === 'ar'
                        ? '1 = عالي، 5 = متوسط، 10 = منخفض'
                        : '1 = High, 5 = Medium, 10 = Low'}
                    </p>
                  </div>
                </div>
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => setIsDialogOpen(false)}
                    disabled={addingLink}
                  >
                    {language === 'ar' ? 'إلغاء' : 'Cancel'}
                  </Button>
                  <Button
                    onClick={handleAddLink}
                    disabled={addingLink || !newUrl.trim()}
                    className="bg-gradient-to-r from-eva-primary to-eva-secondary"
                  >
                    {addingLink ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        {language === 'ar' ? 'جاري الإضافة...' : 'Adding...'}
                      </>
                    ) : (
                      <>
                        <Plus className="w-4 h-4 mr-2" />
                        {language === 'ar' ? 'إضافة' : 'Add'}
                      </>
                    )}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Links Table */}
        <Card className="bg-chat-surface border-chat-border">
          {loading && links.length === 0 ? (
            <div className="p-8 text-center">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-eva-primary" />
              <p className="text-text-secondary">
                {language === 'ar' ? 'جاري التحميل...' : 'Loading...'}
              </p>
            </div>
          ) : filteredLinks.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-text-secondary">
                {language === 'ar' ? 'لا توجد روابط' : 'No links found'}
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{language === 'ar' ? 'الرابط' : 'URL'}</TableHead>
                  <TableHead>{language === 'ar' ? 'العنوان' : 'Title'}</TableHead>
                  <TableHead>{language === 'ar' ? 'المصدر' : 'Source'}</TableHead>
                  <TableHead>{language === 'ar' ? 'التاريخ' : 'Date'}</TableHead>
                  <TableHead>{language === 'ar' ? 'الإجراءات' : 'Actions'}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredLinks.map((link) => (
                  <TableRow key={link.id}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <a
                          href={link.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-eva-primary hover:underline flex items-center gap-1"
                        >
                          {link.url?.substring(0, 50)}
                          {link.url && link.url.length > 50 ? '...' : ''}
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="max-w-xs truncate" title={link.title}>
                        {link.title || '-'}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{link.source || 'general'}</Badge>
                    </TableCell>
                    <TableCell className="text-sm text-text-secondary">
                      {formatDate(link.timestamp)}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => window.open(link.url, '_blank')}
                          title={language === 'ar' ? 'فتح الرابط' : 'Open link'}
                        >
                          <ExternalLink className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </Card>

        {/* Stats */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-chat-surface border-chat-border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">
                  {language === 'ar' ? 'إجمالي الروابط' : 'Total Links'}
                </p>
                <p className="text-2xl font-bold text-eva-primary">{links.length}</p>
              </div>
              <Globe className="w-8 h-8 text-eva-primary opacity-50" />
            </div>
          </Card>
          <Card className="bg-chat-surface border-chat-border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">
                  {language === 'ar' ? 'روابط مع بيانات' : 'Links with Data'}
                </p>
                <p className="text-2xl font-bold text-eva-accent">
                  {links.filter((l) => l.content).length}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-eva-accent opacity-50" />
            </div>
          </Card>
          <Card className="bg-chat-surface border-chat-border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">
                  {language === 'ar' ? 'مصادر مختلفة' : 'Different Sources'}
                </p>
                <p className="text-2xl font-bold text-eva-secondary">
                  {new Set(links.map((l) => l.source).filter(Boolean)).size}
                </p>
              </div>
              <RefreshCw className="w-8 h-8 text-eva-secondary opacity-50" />
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default LinksManagement;

