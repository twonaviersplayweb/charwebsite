var app = angular.module('app', [])

app.controller('my_ctrl', ['$scope','$http', function($scope, $http){
	$scope.hello = 'hello'
	$scope.products = ''
	$scope.loadData = function  () {
		// body...
		$http.get('productData.json').success(function (data) {
			// body...
			$scope.products = data;
			console.log('hello')
			console.log(data)
		})


	}

}])