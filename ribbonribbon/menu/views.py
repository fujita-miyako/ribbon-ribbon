from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import PageForm
from .models import Page
from django.db.models import Q
from functools import reduce
import operator

class IndexView(View):
    #loginアプリのトップページを作動した時に動くメソッド
    #リクエストオブジェクト(ユーザーから送られてきたデータを含む)
    def get(self, request):
        #renderとは画面のレスポンスを返すもの
        return render(
            request, "menu/index.html")

class PageCreateView(View):
    def get(self, request):
        form = PageForm()
        return render(request, "menu/salegoods.html", {"form": form})

    def post(self, request):
        form = PageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("menu:index")
        return render(request, "menu/salegoods.html",{"form": form})



class PageListView(View):
    def get(self, request):
        page_list = Page.objects.all()
        return render(request, "menu/result.html", {"page_list": page_list})

class PageDetailView(View):
    def get(self, request, id):
        page = get_object_or_404(Page, id=id)
        return render(request, "menu/detail_result.html", {"page": page})


class SearchView(View):
    def get(self, request):
        page_list = Page.objects.order_by('-id')  # 'Page' モデルから全てのデータを取得
        keyword = request.GET.get('keyword')

        if keyword:
            exclusion_list = {' ', '　'}  # 空白の除外リスト
            query_list = [word for word in keyword if word not in exclusion_list]

            if query_list:
                query = reduce(operator.and_, [
                    Q(name__icontains=q) | Q(description__icontains=q) for q in query_list
                ])
                page_list = page_list.filter(query)  # キーワードに基づいてフィルタリング

        return render(request, 'menu/result.html', {
            'keyword': keyword,
            'page_list': page_list  # 検索結果を page_list として渡す
        })


#indexにas_view()メソッドを代入。indexクラスを関数に変換
index = IndexView.as_view()
page_create = PageCreateView.as_view()
page_list = PageListView.as_view()
page_detail = PageDetailView.as_view()